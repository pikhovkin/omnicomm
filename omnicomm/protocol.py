import struct

import libscrc

from . import settings
from .commands import commands
from .exceptions import CRCDoesNotMatch, FrameMarkerDoesNotExist
from .commands import Command
from .types import RegFwCmd
from .utils import import_string
from .registry import registry


class Protocol:
    @classmethod
    def pack_crc(cls, crc: int) -> bytes:
        raise NotImplementedError

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int = 0) -> int:
        raise NotImplementedError

    @classmethod
    def decode(cls, data) -> bytes:
        return data[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb')

    @classmethod
    def encode(cls, data) -> bytes:
        return b'\xc0' + data.replace(b'\xdb', b'\xdb\xdd').replace(b'\xc0', b'\xdb\xdc')

    @classmethod
    def make_crc(cls, cmd_id: int, length, data: bytes) -> int:
        crc16 = libscrc.xmodem(struct.pack(f'<BH', cmd_id, length) + data, 0xffff)
        return crc16

    @classmethod
    def pack(cls, cmd: Command, value: dict) -> bytes:
        data = cmd.pack(value)
        length = len(data)
        crc = cls.make_crc(cmd.id, length, data)
        data = struct.pack('<B', cmd.id) + struct.pack('<H', length) + data
        data += cls.pack_crc(crc)
        return cls.encode(data)

    @classmethod
    def unpack(cls, data: bytes) -> tuple[dict, bytes]:
        if data[0] != 0xc0:
            raise FrameMarkerDoesNotExist('Frame marker does not exist')

        data = cls.decode(data)

        cmd_num = struct.unpack_from('<B', data, offset=0)[0]
        length = struct.unpack_from('<H', data, offset=1)[0]
        original_crc = cls.unpack_crc(data, offset=3 + length)
        original_data = data[3: 3 + length]

        crc = cls.make_crc(cmd_num, length, original_data)
        if original_crc != crc:
            raise CRCDoesNotMatch('CRC does not match')

        remain = data[5 + length:]

        value = commands[cmd_num].unpack(original_data)
        return value, remain

    @classmethod
    def register_proto(cls, item: RegFwCmd, module: str) -> None:
        proto_class = import_string(module)
        registry.register(item, proto_class)

    @classmethod
    def load_command_proto(cls) -> None:
        cmd_proto = getattr(settings, 'COMMAND_PROTO', {}) or {}
        for k, v in cmd_proto.items():
            cls.register_proto(k, v)


class RegistrarProtocol(Protocol):
    @classmethod
    def pack_crc(cls, crc: int) -> bytes:
        return struct.pack('>H', crc)

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int=0) -> int:
        return struct.unpack_from('<H', data, offset=offset)[0]


class ServerProtocol(Protocol):
    @classmethod
    def pack_crc(cls, crc: int) -> bytes:
        return struct.pack('<H', crc)

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int = 0) -> int:
        return struct.unpack_from('>H', data, offset=offset)[0]
