import unittest
from omnicomm.interfaces import COMMAND_GET_ARCHIVE, Registar
import time
import asyncio

from omnicomm.protocol import RegistrarProtocol, ServerProtocol
from omnicomm.protocolserver import OmnicommServerProtocol, OmnicommClientProtocol, Registar, Server
from omnicomm.commands import Cmd85, BaseCommand


class MyServer(OmnicommServerProtocol):
    def __init__(self, on_closed, **kwargs) -> None:
        self.on_closed: asyncio.Future = on_closed
        super().__init__(**kwargs)

    def data_received(self, data: bytes) -> None:
        print('server recv', data.hex())
        super().data_received(data)
    
    async def on_connection(self, registar: Registar):
        print('on_connection', registar)
        ident = await registar.get_ident()
        print("ident", ident)
        i = 0
        await registar.start_get_archive(rec_id=0)
        async for value in registar.get_archive():
            print("record", value)
            i += 1
            if i == 2:
                break
        time = await registar.time_request()
        print(time)
        await self.disconnect()

    def on_cmd(self, registar, cmd):
        print('server.on_cmd', cmd.id, cmd.value)

    def connection_lost(self, exc: Exception | None) -> None:
        self.on_closed.set_result(exc)
        return super().connection_lost(exc)

class MyClient(OmnicommClientProtocol):
    def __init__(self, on_closed, **kwargs) -> None:
        self.on_closed: asyncio.Future = on_closed
        super().__init__(**kwargs)

    def data_received(self, data: bytes) -> None:
        print('client recv', data.hex())
        super().data_received(data)

    def connection_lost(self, exc: Exception | None) -> None:
        self.on_closed.set_result(exc)
        return super().connection_lost(exc)
    
    def on_cmd(self, registar, cmd):
        print('client.on_cmd', cmd.id, cmd.value)

    async def on_connection(self, server: Server):
        def sent(fut: asyncio.Future):
            print ('sent', fut.result())
        def on_get_archive(registar, cmd: Cmd85):
            print('got', cmd.id , cmd.value)
            print('send86')
            asyncio.create_task(
                server.send_archive(
                    rec_id=cmd.value['rec_id'],
                    unix_time=time.time()
                )
            ).add_done_callback(sent)
            print('send95')
            asyncio.create_task(
                server.send_archive_live(
                    rec_id=cmd.value['rec_id']+1,
                    unix_time=time.time()
                )
            ).add_done_callback(sent)
        server.subscribe(on_get_archive, COMMAND_GET_ARCHIVE)
        await server.send_ident(reg_id=0, firmware=0)


async def server():
    loop = asyncio.get_running_loop()
    on_closed = asyncio.Future()

    server = await loop.create_server(
        lambda: MyServer(on_closed, auto_time_response=True),
        host='0.0.0.0',
        port=9977)

    async with server:
        print('serving', server)
        await server.start_serving()
        await on_closed
        #await server.serve_forever()


async def client():
    loop = asyncio.get_running_loop()
    #await asyncio.sleep(1)
    on_closed = asyncio.Future()

    transport, protocol = await loop.create_connection(
        lambda: MyClient(on_closed, auto_time_response=True), host="127.0.0.1", port=9977)

    await on_closed
    transport.close()


async def main():
    server_task = asyncio.create_task(server())
    client_task = asyncio.create_task(client())

    await asyncio.gather(server_task, client_task)


class TestServer(unittest.TestCase):

    def test_server_client(self):
        ServerProtocol.load_command_proto()
        asyncio.run(main())
