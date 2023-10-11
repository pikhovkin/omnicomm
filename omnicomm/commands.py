import struct
import time

from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message

from omnicomm.exceptions import CommandAlreadyExistsError
from omnicomm.registry import reg_fw_cmd

Command = type['BaseCommand']


class BaseCommand:
    id: int = 0  # noqa: A003
    format: str = ''  # noqa: A003

    BASE_TIME: int = 1230768000

    def __init__(self, value: dict) -> None:
        self.value: dict = value

    @classmethod
    def to_unix_time(cls, omnicomm_time: int) -> int:
        return cls.BASE_TIME + omnicomm_time

    @classmethod
    def to_omnicomm_time(cls, unix_time: int | None) -> int:
        if unix_time is None:
            unix_time = int(time.time())
        omnicomm_time = unix_time - cls.BASE_TIME
        if omnicomm_time < 0:
            omnicomm_time = 0
        return omnicomm_time

    @classmethod
    def pack_protobuf(cls, value: dict, proto_class: type[Message]) -> bytes:
        proto_instance: Message = ParseDict(value, proto_class())
        return proto_instance.SerializeToString()

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:
        raise NotImplementedError()

    def pack(self, conf: dict | None = None) -> bytes:
        return struct.pack(f'<{self.format}', *self.from_dict(self.value, conf or {}))

    @classmethod
    def unpack_protobuf(cls, data: bytes, proto_class: type[Message]):
        proto_instance = proto_class()
        proto_instance.ParseFromString(data)
        return MessageToDict(proto_instance)

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:
        raise NotImplementedError()

    @classmethod
    def unpack(cls, data: bytes, conf: dict | None = None) -> 'BaseCommand':
        return cls(cls.to_dict(struct.unpack_from(cls.format, data), conf or {}))


class Cmd80(BaseCommand):
    id: int = 0x80  # noqa: A003
    format: str = 'II'  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        return value.get('reg_id', 0) or 0, value.get('firmware', 0) or 0

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return dict(reg_id=value[0], firmware=value[1])


class Cmd81(BaseCommand):
    id: int = 0x81  # noqa: A003
    format: str = 'II'  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        return value.get('server_id', 0) or 0, value.get('server_ver', 0) or 0


class Cmd85(BaseCommand):
    id: int = 0x85  # noqa: A003
    format: str = 'I'  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        return (value.get('rec_id', 0) or 0,)

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return dict(rec_id=value[0])


class Cmd86(BaseCommand):
    id: int = 0x86  # noqa: A003
    format: str = 'IIB'  # noqa: A003

    # @classmethod
    # def to_datetime(cls, omnicomm_time):
    #     return datetime(*tuple(time.gmtime(cls.to_unix_time(omnicomm_time)))[:6])

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        omnicomm_time = value.get('omnicomm_time', 0) or cls.to_omnicomm_time(value.get('unix_time', None))
        return value['rec_id'], int(omnicomm_time), value['priority']

    def pack(self, conf: dict | None = None) -> bytes:
        msgs: list | None = self.value.get('msgs')
        if not msgs:
            return b''

        reg_id, fw = self.value.get('reg_id', 0), self.value.get('firmware', 0)
        proto_class: type[Message] = reg_fw_cmd[(reg_id, fw, self.id)]

        data = b''
        for msg in msgs:
            _msg = self.pack_protobuf(msg, proto_class)
            length = len(_msg)
            data += struct.pack('<H', length)
            data += _msg

        return struct.pack(f'<{self.format}', *self.from_dict(self.value, conf or {})) + data

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return dict(rec_id=value[0], omnicomm_time=value[1], priority=value[2], unix_time=cls.to_unix_time(value[1]))

    @classmethod
    def unpack(cls, data: bytes, conf: dict | None = None) -> BaseCommand:
        if not data:
            return cls({})

        rec_id, omnicomm_time, priority = struct.unpack_from(cls.format, data)
        value: dict = cls.to_dict(
            (
                rec_id,
                omnicomm_time,
                priority,
            ),
            conf or {},
        )

        data = data[9:]

        reg_id, fw = (conf or {}).get('reg_id', 0), (conf or {}).get('firmware', 0)
        proto_class: type[Message] = reg_fw_cmd[(reg_id, fw, cls.id)]

        msgs = []
        while data:
            length = struct.unpack_from('<H', data)[0]
            proto_data = cls.unpack_protobuf(data[2 : 2 + length], proto_class)
            msgs.append(proto_data)
            data = data[2 + length :]

        value.update(dict(msgs=msgs))
        return cls(value)


class Cmd87(BaseCommand):
    id: int = 0x87  # noqa: A003
    format: str = 'I'  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        return (value.get('rec_id', 0) or 0,)

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return dict(rec_id=value[0])


class Cmd88(BaseCommand):
    id: int = 0x88  # noqa: A003
    format: str = 'I'  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        return (value.get('rec_id', 0) or 0,)

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return dict(rec_id=value[0])


# class Cmd89(BaseCommand):
#     id: int = 0x89
#
#
# class Cmd8A(BaseCommand):
#     id: int = 0x8A
#
#
# class Cmd8B(BaseCommand):
#     id: int = 0x8B
#
#
# class Cmd8C(BaseCommand):
#     id: int = 0x8C
#
#
# class Cmd8D(BaseCommand):
#     id: int = 0x8D
#
#
# class Cmd8E(BaseCommand):
#     id: int = 0x8E
#
#
# class Cmd8F(BaseCommand):
#     id: int = 0x8F
#
#
# class Cmd90(BaseCommand):
#     id: int = 0x90
#
#
# class Cmd91(BaseCommand):
#     id: int = 0x91
#
#
# class Cmd92(BaseCommand):
#     id: int = 0x92


class Cmd93(BaseCommand):
    id: int = 0x93  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        return tuple()

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return {}


class Cmd94(BaseCommand):
    id: int = 0x94  # noqa: A003
    format: str = 'I'  # noqa: A003

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:  # noqa: ARG003
        omnicomm_time = value.get('omnicomm_time', 0) or cls.to_omnicomm_time(value.get('unix_time', None))
        return (int(omnicomm_time),)

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:  # noqa: ARG003
        return dict(omnicomm_time=value[0], unix_time=cls.to_unix_time(value[0]))


class Cmd95(Cmd86):
    id: int = 0x95  # noqa: A003


# class Cmd96(BaseCommand):
#     id: int = 0x96
#
#
# class Cmd97(BaseCommand):
#     id: int = 0x97
#
#
# class Cmd98(BaseCommand):
#     id: int = 0x99
#
#
# class Cmd99(BaseCommand):
#     id: int = 0x99
#
#
# class Cmd9A(BaseCommand):
#     id: int = 0x9A
#
#
# class Cmd9B(BaseCommand):
#     id: int = 0x9B
#
#
# class Cmd9C(BaseCommand):
#     id: int = 0x9C
#
#
# class Cmd9D(BaseCommand):
#     id: int = 0x9D
#
#
# class Cmd9E(BaseCommand):
#     id: int = 0x9E


class Cmd9F(Cmd86):
    id: int = 0x9F  # noqa: A003


class CmdA0(Cmd87):
    id: int = 0xA0  # noqa: A003


commands = {}
_command_classes = BaseCommand.__subclasses__()
while _command_classes:
    _cmd = _command_classes.pop(0)
    if _cmd.id in commands:
        msg = 'Command ID already exists'
        raise CommandAlreadyExistsError(msg)
    commands[_cmd.id] = _cmd
    _command_classes.extend(_cmd.__subclasses__())


__all__ = tuple([cmd.__name__ for cmd in commands.values()])
