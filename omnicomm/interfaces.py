from omnicomm.protocol import RegistrarProtocol, ServerProtocol, UnpackingCRCError, Protocol
from omnicomm.commands import BaseCommand, Cmd93, Cmd94, Cmd81, Cmd87, Cmd80, Cmd85, Cmd86, Cmd88, Cmd95

import time
import asyncio

from collections import defaultdict

import io


COMMAND_GET_ARCHIVE = 0x85


class InterfaceBase:
    writer: io.IOBase | asyncio.WriteTransport
    protocol = Protocol

    def subscribe(self, cb, *ids):
        for i in ids:
            self.on_cmd_callbacks[i].add(cb)

    def unsubscribe(self, cb, *ids):
        for i in ids:
            self.on_cmd_callbacks[i].remove(cb)

    def on_time_request(self, cmd: Cmd93):
        if self.auto_time_response:
            self.send_cmd(
                Cmd94({'unix_time': time.time()})
            )

    def on_time_response(self, cmd: Cmd94):
        pass

    async def time_request(self):
        res = asyncio.Future()

        def time_request_cb(r, c:Cmd94):
            res.set_result(c.value)
        self.subscribe(time_request_cb, 0x94)
        try:
            self.send_cmd(
                Cmd93({})
            )
            return await res
        finally:
            self.unsubscribe(time_request_cb, 0x94)

    cmd_index = {
        0x93: on_time_request,
        0x94: on_time_response,
    }

    def on_cmd(self, cmd: BaseCommand):
        class_cb = self.cmd_index.get(cmd.id)
        if class_cb:
            class_cb(self, cmd)
        for cb in self.on_cmd_callbacks[cmd.id]:
            cb(self, cmd)
        for cb in self.on_cmd_callbacks[None]:
            cb(self, cmd)

    def __init__(self, writer: io.IOBase | asyncio.WriteTransport, on_cmd=None, ident=None, auto_time_response: bool = False):
        self.my_ident = ident or dict()
        self.remain = b''
        self.writer = writer
        self.auto_time_response = auto_time_response
        self.on_cmd_callbacks = defaultdict(set)
        if on_cmd:
            self.on_cmd_callbacks[None].add(on_cmd)
        self.ident = asyncio.Future()

    def pack(self, cmd):
        return self.protocol.pack(cmd)

    def send_cmd(self, cmd):
        return self.writer.write(
            self.protocol.pack(cmd)
        )

    def feed(self, data):
        self.remain += data
        cmds = []
        try:
            cmds, self.remain = self.protocol.unpack_many(self.remain)
        except UnpackingCRCError as e:
            pass
        for cmd in cmds:
            self.on_cmd(cmd)


class Server(InterfaceBase):
    protocol = RegistrarProtocol

    def on_identify(self, cmd: Cmd81):
        self.ident.set_result(cmd.value)

    def on_get_archive(self, cmd: Cmd85):
        pass

    def on_delete(self, cmd: Cmd87):
        pass

    async def send_ident(self, reg_id: int, firmware: int):
        value = {"reg_id": reg_id, "firmware": firmware}
        self.send_cmd(
            Cmd80(value)
        )

    async def send_archive(self, rec_id=None, msgs=None, priority=0, omnicomm_time=None, unix_time=None, cmd=Cmd86):
        if not (omnicomm_time or unix_time):
            raise Exception('omnicomm_time or unix_time required')
        value = {
            'rec_id': rec_id,
            'msgs': msgs,
            'priority': priority,
            'omnicomm_time': omnicomm_time,
            'unix_time': unix_time
        }

        self.send_cmd(
            cmd(value)
        )

    async def send_archive_live(self,  rec_id=None, msgs=None, priority=0, omnicomm_time=None, unix_time=None):
        return await self.send_archive(rec_id, msgs, priority, omnicomm_time, unix_time, cmd=Cmd95)

    async def delete_ack(self, rec_id: int):
        self.send_cmd(
            Cmd88({"rec_id": rec_id})
        )

    cmd_index = InterfaceBase.cmd_index.copy()
    cmd_index.update({
        0x81: on_identify,
        0x85: on_get_archive,
        0x87: on_delete,
    })


class Registar(InterfaceBase):
    protocol = ServerProtocol

    async def get_ident(self):
        return await self.ident

    async def delete(self, rec_id):
        res = asyncio.Future()

        def delete_cb(r, c: Cmd88):
            res.set_result(c.value)

        self.subscribe(delete_cb, 0x88)
        try:
            self.send_cmd(
                Cmd87({'rec_id': rec_id})
            )
            return (await res)
        finally:
            self.unsubscribe(delete_cb, 0x88)

    async def start_get_archive(self, rec_id: int):
        return self.send_cmd(Cmd85({'rec_id': rec_id}))

    async def get_archive(self, autodelete_each: bool = False, autodelete_last: bool = False):
        queue = asyncio.Queue()
        def get_archive_cb(r:Registar, c: Cmd86 | Cmd95):
            queue.put_nowait(c.value)
        self.subscribe(get_archive_cb, 0x86, 0x95)
        value = {}
        try:
            while True:
                value = await queue.get()
                yield value
                if autodelete_each:
                    await self.delete(rec_id=value['rec_id'])
        finally:
            if autodelete_last and value:
                await self.delete(rec_id=value['rec_id'])

            self.unsubscribe(get_archive_cb, 0x86, 0x95)

    def on_identify(self, cmd: Cmd80):
        self.ident.set_result(cmd.value)

    def on_archive(self, cmd: Cmd86 | Cmd95):
        pass

    def on_delete_ack(self, cmd: Cmd88):
        pass

    def on_firmware_block(self, cmd: BaseCommand):
        raise NotImplementedError(cmd)

    def on_firmware_update(self, cmd: BaseCommand):
        raise NotImplementedError(cmd)

    def on_settings(self, cmd: BaseCommand):
        raise NotImplementedError(cmd)

    def on_settings_write(self, cmd: BaseCommand):
        raise NotImplementedError(cmd)

    def on_extended_settings(self, cmd: BaseCommand):
        pass

    def on_extended_settings_write(self, cmd: BaseCommand):
        pass

    def on_set_encription(self, cmd: BaseCommand):
        if cmd.value == 0:
            self.encrypted = True

    cmd_index = InterfaceBase.cmd_index.copy()
    cmd_index.update({
        0x80: on_identify,
        0x86: on_archive,
        0x88: on_delete_ack,
        0x95: on_archive,
    })
