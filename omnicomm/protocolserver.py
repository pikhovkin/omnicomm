import asyncio
from omnicomm.interfaces import Registar, Server


class OmnicommProtocol(asyncio.Protocol):

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        super().__init__()

    def on_cmd(self, registar, cmd):
        "hook on cmd recieved"
        pass

    async def on_connection(self, registar):
        "hook on connection"
        pass

    async def disconnect(self):
        self.transport.close()

    def connection_made(self, transport):
        self.transport = transport

class OmnicommServerProtocol(OmnicommProtocol):

    def connection_made(self, transport):
        super().connection_made(transport)
        self.registar = Registar(writer=self.transport, on_cmd=self.on_cmd, **self.kwargs) # type: ignore
        asyncio.create_task(self.on_connection(self.registar))

    def data_received(self, data: bytes) -> None:
        self.registar.feed(data)


class OmnicommClientProtocol(OmnicommProtocol):

    def connection_made(self, transport):
        super().connection_made(transport)
        self.server = Server(writer=self.transport, on_cmd=self.on_cmd, **self.kwargs) # type: ignore
        asyncio.create_task(self.on_connection(self.server))

    def data_received(self, data: bytes) -> None:
        self.server.feed(data)
