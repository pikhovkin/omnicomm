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
            key = tuple(filter(bool, item))
            if len(key) == 3:
                reg_id, fw, cmd = key
                return self._registry.get(key, None) or self._registry.get((reg_id, cmd), None) or self._registry.get(cmd, None)
            elif len(key) == 2:
                reg_id, cmd = key
                return self._registry.get(key, None) or self._registry.get(cmd, None)
            elif len(key) == 1:
                return self._registry.get(key[0], None)


registry = Registry()
