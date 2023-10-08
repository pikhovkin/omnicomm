from omnicomm.protocolserver import OmnicommServerProtocol

class MyServer(OmnicommServerProtocol):
    def on_connection(self, registar):
        print('on_connection', registar)
        ident = await registar.get_ident()
        async for value in registar.get_archive(rec_id=0):
            print("record", value['rec_id'])

    def on_cmd(self, cmd):
        print('on_cmd', cmd.id, cmd.value)

    


async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 9977)

    async with server:
        await server.serve_forever()


ServerProtocol.load_command_proto()

asyncio.run(main())