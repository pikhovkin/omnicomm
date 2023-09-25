from google.protobuf.message import Message

from omnicomm.exceptions import ProtoDoesNotExistError
from omnicomm.types import RegFwCmd


class RegFwCmdRegistry:
    def __init__(self) -> None:
        self._registry: dict[int | RegFwCmd, type[Message]] = {}

    def __getitem__(self, item: int | RegFwCmd) -> type[Message]:
        proto_cls: type[Message] | None = None
        if isinstance(item, int):
            proto_cls = self._registry.get(item, None)
        elif isinstance(item, tuple):
            key: RegFwCmd = tuple(filter(bool, item))
            if len(key) == 3:  # noqa: PLR2004
                reg_id, fw, cmd = key
                proto_cls = (
                    self._registry.get(key, None)
                    or self._registry.get((reg_id, cmd), None)
                    or self._registry.get(cmd, None)
                )
            elif len(key) == 2:  # noqa: PLR2004
                reg_id, cmd = key
                proto_cls = self._registry.get(key, None) or self._registry.get(cmd, None)
            elif len(key) == 1:
                proto_cls = self._registry.get(key[0], None)

        if proto_cls is None:
            msg = 'Proto file does not exist'
            raise ProtoDoesNotExistError(msg)

        return proto_cls

    def clear(self):
        self._registry = {}

    def register(self, key: int | RegFwCmd, proto_class: type[Message]) -> None:
        self._registry[key] = proto_class

    def unregister(self, key: int | RegFwCmd) -> None:
        self._registry.pop(key, None)


reg_fw_cmd = RegFwCmdRegistry()
