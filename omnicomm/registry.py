from google.protobuf.message import Message

from .types import RegFwCmd


class Registry:
    def __init__(self) -> None:
        self._registry: dict[RegFwCmd, type[Message]] = {}

    def register(self, key: RegFwCmd, proto_class: type[Message]) -> None:
        self._registry[key] = proto_class

    def unregister(self, key: RegFwCmd) -> None:
        self._registry.pop(key, None)

    def __getitem__(self, item: RegFwCmd):
        if isinstance(item, int):
            return self._registry.get(item, None)
        elif isinstance(item, tuple):
            if len(item) == 3:
                reg_id, fw, cmd = item
                return self._registry.get(item, self._registry.get((reg_id, cmd), self._registry.get(cmd, None)))
            elif len(item) == 2:
                reg_id, cmd = item
                return self._registry.get(item, self._registry.get(cmd, None))


registry = Registry()
