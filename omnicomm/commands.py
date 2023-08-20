from datetime import datetime
import struct
import time

from google.protobuf.message import Message
from google.protobuf.json_format import MessageToDict, ParseDict

from .exceptions import CommandAlreadyExists
from .registry import registry


class BaseCommand:
    id: int = 0
    format: str = ''

    @classmethod
    def pack_protobuf(cls, value: dict, proto_class: type[Message]):
        proto_instance: type[Message] = ParseDict(value, proto_class())
        return proto_instance.SerializeToString()

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:
        raise NotImplementedError

    @classmethod
    def pack(cls, value: dict, conf: dict | None = None) -> bytes:
        return struct.pack(f'<{cls.format}', *cls.from_dict(value, conf or {}))

    @classmethod
    def unpack_protobuf(cls, data: bytes, proto_class: type[Message]):
        proto_instance = proto_class()
        proto_instance.ParseFromString(data)
        return MessageToDict(proto_instance)

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:
        raise NotImplementedError

    @classmethod
    def unpack(cls, data: bytes, conf: dict | None = None) -> dict:
        return cls.to_dict(struct.unpack_from(cls.format, data), conf or {})


Command = type[BaseCommand]


class Cmd80(BaseCommand):
    id: int = 0x80
    format: str = 'II'

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:
        return dict(reg_id=value[0], firmware=value[1])


class Cmd81(BaseCommand):
    id: int = 0x81
    format: str = 'II'

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:
        return (value.get('server_id', 0) or 0, value.get('server_ver', 0) or 0,)


class Cmd85(BaseCommand):
    id: int = 0x85
    format: str = 'I'

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:
        return (value.get('rec_num', 0) or 0,)


class Cmd86(BaseCommand):
    id: int = 0x86
    format: str = 'IIB'

    # BASE_TIME = 1230768000
    #
    # @classmethod
    # def to_unix_time(cls, omnicomm_time):
    #     return cls.BASE_TIME + omnicomm_time
    #
    # @classmethod
    # def to_datetime(cls, omnicomm_time):
    #     return datetime(*tuple(time.gmtime(cls.to_unix_time(omnicomm_time)))[:6])

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:
        raise NotImplementedError

    @classmethod
    def pack(cls, value: dict, conf: dict | None = None) -> bytes:
        return struct.pack(f'<{cls.format}', *cls.from_dict(value, conf or {}))

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:
        return dict(num_rec=value[0], omnicomm_time=value[1], priority=value[2])

    @classmethod
    def unpack(cls, data: bytes, conf: dict | None = None) -> dict:
        num_rec, omnicomm_time, priority = struct.unpack_from(cls.format, data)
        value: dict = cls.to_dict((num_rec, omnicomm_time, priority,), conf or {})

        data = data[9:]

        reg_id, fw =  conf.get('reg_id'), conf.get('firmware')
        proto_class: type[Message] = registry[(reg_id, fw, cls.id)]

        msgs = []
        while data:
            length = struct.unpack_from('<H', data)[0]
            proto_data = cls.unpack_protobuf(data[2:2 + length], proto_class)
            msgs.append(proto_data)
            data = data[2 + length:]

        value.update(dict(msgs=msgs))
        return value


class Cmd87(BaseCommand):
    id: int = 0x87
    format: str = 'I'

    @classmethod
    def from_dict(cls, value: dict, conf: dict) -> tuple[int, ...]:
        return (value.get('rec_num', 0) or 0,)


class Cmd88(BaseCommand):
    id: int = 0x88
    format: str = 'I'

    @classmethod
    def to_dict(cls, value: tuple[int, ...], conf: dict) -> dict:
        return dict(rec_num=value[0])


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
#
#
# class Cmd93(BaseCommand):
#     id: int = 0x93
#
#
# class Cmd94(BaseCommand):
#     id: int = 0x94


class Cmd95(Cmd86):
    id: int = 0x95


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
#
#
# class Cmd9F(BaseCommand):
#     id: int = 0x9F
#
#
# class CmdA0(BaseCommand):
#     id: int = 0xA0


commands = {}
_command_classes = BaseCommand.__subclasses__()
while _command_classes:
    _cmd = _command_classes.pop(0)
    if _cmd.id in commands:
        raise CommandAlreadyExists('Command ID already exists')
    commands[_cmd.id] = _cmd
    _command_classes.extend(_cmd.__subclasses__())


__all__ = tuple(commands.values())
