from omnicomm.interfaces import Registar


import asyncio

from omnicomm import commands
from omnicomm.protocol import RegistrarProtocol, ServerProtocol        
from omnicomm.protocolserver import OmnicommServerProtocol,OmnicommClientProtocol, Registar, Server
from omnicomm.commands import Cmd85

class MyServer(OmnicommServerProtocol):
    async def on_connection(self, registar:Registar):
        print('on_connection', registar)
        ident = await registar.get_ident()
        print("ident", ident)
        async for value in registar.get_archive(rec_id=0):
            print("record", value['rec_id'])

    def on_cmd(self, cmd):
        print('on_cmd', cmd.id, cmd.value)


class MyClient(OmnicommClientProtocol):
    async def on_connection(self, server: Server):
        def on_get_archive(server: Server, cmd:Cmd85):
            asyncio.create_task(server.send_archive(rec_id=cmd.value['rec_id']))
        server.on_get_archive = on_get_archive
        await server.send_ident(reg_id=0,firmware=0)
        

async def server():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: MyServer(),
        '0.0.0.0', 9977)
    ServerProtocol.load_command_proto()
    async with server:
        print('serving', server)
        await server.serve_forever()

async def client():
    loop = asyncio.get_running_loop()
    client = loop.create_connection(lambda: MyClient())


async def main():
    server_task = asyncio.create_task(server())
    client_task = asyncio.create_task(client())

    await asyncio.gather(server_task, client_task)

if __name__ == "__main__":
    asyncio.run(main())