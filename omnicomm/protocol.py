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
    def pack_crc(cls, crc: int):
        raise NotImplementedError

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int = 0):
        raise NotImplementedError

    @classmethod
    def decode(cls, data):
        return data[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb')

    @classmethod
    def encode(cls, data):
        return b'\xc0' + data.replace(b'\xdb', b'\xdb\xdd').replace(b'\xc0', b'\xdb\xdc')

    @classmethod
    def make_crc(cls, cmd_id: int, length, data: bytes):
        crc16 = libscrc.xmodem(struct.pack(f'<BH', cmd_id, length) + data, 0xffff)
        return crc16

    @classmethod
    def pack(cls, cmd: Command, value: dict):
        data = cmd.pack(value)
        length = len(data)
        crc = cls.make_crc(cmd.id, length, data)
        data = struct.pack('<B', cmd.id) + struct.pack('<H', length) + data
        data += cls.pack_crc(crc)
        return cls.encode(data)

    @classmethod
    def unpack(cls, data: bytearray):
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

        cmd = commands[cmd_num].unpack(original_data)
        return cmd, remain

    @classmethod
    def register_proto(cls, item: RegFwCmd, module: str):
        proto_class = import_string(module)
        registry.register(item, proto_class)

    @classmethod
    def load_command_proto(cls):
        cmd_proto = getattr(settings, 'COMMAND_PROTO', {}) or {}
        for k, v in cmd_proto.items():
            cls.register_proto(k, v)


class RegisterProtocol(Protocol):
    @classmethod
    def pack_crc(cls, crc: int):
        return struct.pack('>H', crc)

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int=0):
        return struct.unpack_from('<H', data, offset=offset)[0]


class ServerProtocol(Protocol):
    @classmethod
    def pack_crc(cls, crc: int):
        return struct.pack('<H', crc)

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int = 0):
        return struct.unpack_from('>H', data, offset=offset)[0]
