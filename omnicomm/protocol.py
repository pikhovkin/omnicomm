import struct

import libscrc

from . import settings
from .commands import commands
from .exceptions import CRCDoesNotMatch, FrameMarkerDoesNotExist
from .commands import Command
from .types import RegFwCmd
from .utils import import_string
from .registry import registry


class Omnicomm:
    @classmethod
    def decode(cls, data):
        return data[1:].replace(b'\xdb\xdc', b'\xc0').replace(b'\xdb\xdd', b'\xdb')

    @classmethod
    def encode(cls, data):
        return b'\xc0' + data.replace(b'\xdb', b'\xdb\xdd').replace(b'\xc0', b'\xdb\xdc')

    @classmethod
    def make_crc(cls, cmd: Command, length, data):
        crc16 = libscrc.xmodem(struct.pack(f'<BH', cmd, length) + data, 0xffff)
        return crc16

    def pack(self, cmd: Command):
        ...

    def unpack(self, cmd: Command):
        ...

    def parse(self, data: bytearray):
        if data[0] != 0xc0:
            raise FrameMarkerDoesNotExist('Frame marker does not exist')

        data = self.decode(data)

        cmd_num = struct.unpack_from('<B', data, offset=0)[0]
        length = struct.unpack_from('<H', data, offset=1)[0]
        original_crc = struct.unpack_from('>H', data, offset=3 + length)[0]
        original_data = data[3: 3 + length]

        crc = self.make_crc(cmd_num, length, original_data)
        if original_crc != crc:
            raise CRCDoesNotMatch('CRC does not match')

        remain = data[5 + length:]

        cmd = commands[cmd_num].decode(original_data)
        return cmd, remain

    @classmethod
    def register_proto(cls, item: RegFwCmd, module: str):
        proto_class = import_string(module)
        registry.register(item, proto_class)

    @classmethod
    def load_command_proto(cls):
        cmd_proto = getattr(settings, 'COMMAND_PROTO', {}) or {}
        for k, v in cmd_proto:
            cls.register_proto(k, v)
