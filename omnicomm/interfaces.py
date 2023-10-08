from omnicomm.protocol import RegistrarProtocol, ServerProtocol, UnpackingCRCError
from omnicomm.commands import *

import time
import asyncio

from collections import defaultdict

import io

class InterfaceBase:
    writer: io.IOBase

    def subscribe(self, cb, *ids):
        for i in ids:
            self.on_cmd_callbacks[i].add(cb)

    def unsubscribe(self, cb, *ids):
        for i in ids:
            self.on_cmd_callbacks[i].remove(cb)

    def on_time_request(self, cmd:Cmd93):
        self.writer.write(
            ServerProtocol.pack(
                Cmd94({'unix_time': time.time()})
            )
        )

    def on_time_response(self, cmd:Cmd94):
        pass


    async def time_request(self):
        res = asyncio.Future()
        self.subscribe(res.set_result, 0x94)
        try:
            self.writer.write(
                ServerProtocol.pack(
                    Cmd93()
                )
            )
            return await res
        finally:
            self.unsubscribe(res.set_result, 0x94)

    def on_cmd(self, cmd:BaseCommand):
        class_cb = self.cmd_index.get(cmd.id)
        if class_cb: class_cb(cmd)
        for cb in self.on_cmd_callbacks[cmd.id]:
            cb(cmd)        
        for cb in self.on_cmd_callbacks[None]:
            cb(cmd)

    def __init__(self, writer, on_cmd=None, ident=None):
        self.my_ident = ident or dict()
        self.remain=b''
        self.writer = writer
        self.on_cmd_callbacks = defaultdict(set)
        if on_cmd:
            self.on_cmd_callbacks[None].add(on_cmd)
        self.ident = asyncio.Future()


    def feed(self, data):
        self.remain += data
        try:
            cmds, self.remain = ServerProtocol.unpack_many(self.remain)
        except UnpackingCRCError as e:
            pass
        for cmd in cmds:
            self.on_cmd(cmd)


class Server(InterfaceBase):
   
    def on_identify(self, cmd: Cmd81):
        self.ident.set_result(cmd.value)
        
    def on_get_archive(self, cmd:Cmd85):
        pass
    
    def on_delete(self, cmd: Cmd87):
        self.delete_ack(cmd.value)
    
    async def send_ident(self, reg_id: int, firmware: int):
        value = {"reg_id":reg_id, "firmware": firmware}
        self.writer.write(
            ServerProtocol.pack(
                Cmd80(value)
            )
        )

    async def send_archive(self, rec_id=None, msgs=None, priority=None, omnicomm_time=None, unix_time=None, cmd=Cmd86):
        value = {
            'rec_id':rec_id, 
            'msgs':msgs, 
            'priority':priority, 
            'omnicomm_time':omnicomm_time, 
            'unix_time':unix_time
        }
        
        self.writer.write(
            ServerProtocol.pack(
                cmd(value)
            )            
        )

    async def send_archive_live(self,  rec_id=None, msgs=None, priority=None, omnicomm_time=None, unix_time=None):
        return self.send_archive( rec_id, msgs, priority, omnicomm_time, unix_time, cmd=Cmd95)


    async def delete_ack(self, rec_id:int):
        self.writer.write(
            ServerProtocol.pack(
                Cmd88({"rec_id":rec_id})
            )
        )

class Registar(InterfaceBase):

    async def get_ident(self):
        return await self.ident

    async def delete(self, rec_id):
        res = asyncio.Future()
        self.subscribe( res.set_result, 0x88 )
        try:
            self.writer.write(
                ServerProtocol.pack(
                    Cmd94({'unix_time': time.time()})
                )
            )
            return await res
        finally:
            self.unsubscribe( res.set_result, 0x88 )


    async def get_archive(self, rec_id: int, autodelete_each: bool=False, autodelete_last: bool=False):
        queue = asyncio.Queue()
        self.subscribe( queue.put_nowait , 0x86, 0x95 )
        cmd: BaseCommand = None
        try:
            data = ServerProtocol.pack(Cmd85({'rec_id': rec_id}))
            self.writer.write(data)
            while True:
                cmd = await queue.get()
                yield cmd
                if autodelete_each:
                    await self.delete(rec_id=cmd.value['rec_id'])
        finally:
            if autodelete_last and cmd:
                await self.delete(rec_id=cmd.value['rec_id'])
            self.unsubscribe(queue.put_nowait , 0x86, 0x95)

    def on_identify(self, cmd: Cmd80):
        self.ident.set_result(cmd.value)

    def on_archive(self, cmd: Cmd86|Cmd95):
        pass

    def on_delete_ack(self, cmd: Cmd88):
        pass

    def on_firmware_block(self, cmd:BaseCommand):
        raise NotImplementedError(cmd)

    def on_firmware_update(self, cmd:BaseCommand):
        raise NotImplementedError(cmd)

    def on_settings(self, cmd:BaseCommand):
        raise NotImplementedError(cmd)

    def on_settings_write(self, cmd:BaseCommand):
        raise NotImplementedError(cmd)

    def on_extended_settings(self, cmd:BaseCommand):
        pass

    def on_extended_settings_write(self, cmd:BaseCommand):
        pass

    def on_set_encription(self, cmd:BaseCommand):
        if cmd.value == 0:
            self.encrypted = True

    cmd_index = {
        0x80:on_identify,
        0x86:on_archive,
        0x88:on_delete_ack,
        0x93:InterfaceBase.on_time_request,
        0x94:InterfaceBase.on_time_response,
        0x95:on_archive,
    }

