import asyncio
from omnicomm.interfaces import Registar, Server

class OmnicommServerProtocol(asyncio.Protocol):

    def on_cmd(self, registar, cmd):
        "hook on cmd recieved"
        pass

    async def on_connection(self, registar):
        "hook on connection"
        pass

    def connection_made(self, transport):
        self.transport = transport
        self.registar = Registar(writer=self.transport, on_cmd=self.on_cmd)
        asyncio.create_task(self.on_connection(self.registar))
    
    def data_received(self, data: bytes) -> None:
        self.registar.feed(data)

class OmnicommClientProtocol(asyncio.Protocol):

    def on_cmd(self, server, cmd):
        "hook on cmd recieved"
        pass

    async def on_connection(self, server: Server):
        "hook on connection"

    def connection_made(self, transport):
        self.transport = transport
        self.server = Server(writer=self.transport, on_cmd=self.on_cmd)
        asyncio.create_task(self.on_connection(self.server))
    
    def data_received(self, data: bytes) -> None:
        self.server.feed(data)

