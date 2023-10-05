import struct

import libscrc

from omnicomm import settings
from omnicomm.commands import BaseCommand, commands
from omnicomm.exceptions import (CRCDoesNotMatchError, EmptyDataError,
                                 FrameMarkerDoesNotExistError,
                                 UnpackingCRCError)
from omnicomm.registry import reg_fw_cmd
from omnicomm.types import RegFwCmd
from omnicomm.utils import import_string

FRAME_MARKER = b'\xc0'


class Protocol:
    @classmethod
    def pack_crc(cls, crc: int) -> bytes:
        raise NotImplementedError

    @classmethod
    def unpack_crc(cls, data: bytes, offset: int = 0) -> int:
        raise NotImplementedError

    @classmethod
    def decode(cls, data) -> bytes:
        return data[1:].replace(b'\xdb\xdc', FRAME_MARKER).replace(b'\xdb\xdd', b'\xdb')

    @classmethod
    def encode(cls, data) -> bytes:
        return FRAME_MARKER + data.replace(b'\xdb', b'\xdb\xdd').replace(FRAME_MARKER, b'\xdb\xdc')

    @classmethod
    def make_crc(cls, cmd_id: int, length, data: bytes) -> int:
        crc16 = libscrc.xmodem(struct.pack('<BH', cmd_id, length) + data, 0xffff)
        return crc16

    @classmethod
    def pack(cls, cmd: BaseCommand) -> bytes:
        data = cmd.pack()
        length = len(data)
        crc = cls.make_crc(cmd.id, length, data)
        data = struct.pack('<B', cmd.id) + struct.pack('<H', length) + data
        data += cls.pack_crc(crc)
        return cls.encode(data)

    @classmethod
    def unpack(cls, data: bytes) -> tuple[BaseCommand, bytes]:
        if not data:
            msg = 'Data does not exist'
            raise EmptyDataError(msg)
        elif data[0] != FRAME_MARKER[0]:
            msg = 'Frame marker does not exist'
            raise FrameMarkerDoesNotExistError(msg)

        another_frame_idx = data[1:].find(FRAME_MARKER)
        remain = data[another_frame_idx + 1:] if another_frame_idx > -1 else b''

        data = cls.decode(data[:another_frame_idx + 1] if another_frame_idx > -1 else data)

        cmd_num = struct.unpack_from('<B', data, offset=0)[0]
        length = struct.unpack_from('<H', data, offset=1)[0]
        try:
            original_crc = cls.unpack_crc(data, offset=3 + length)
        except struct.error as err:
            msg = 'More data is required to unpack'
            raise UnpackingCRCError(msg) from err

        original_data = data[3: 3 + length]

        crc = cls.make_crc(cmd_num, length, original_data)
        if original_crc != crc:
            msg = 'CRC does not match'
            raise CRCDoesNotMatchError(msg)

        cmd = commands[cmd_num].unpack(original_data)
        return cmd, remain

    @classmethod
    def unpack_many(cls, data: bytes) -> tuple[[BaseCommand], bytes]:
        cmds = []
        remain = b''
        try:
            while 1:
                cmd, remain = cls.unpack(data)
                cmds.append(cmd)
                data = remain
        except Exception as err:
            if not cmds:
                raise err
        return cmds, remain

    @classmethod
    def register_proto(cls, item: RegFwCmd, module: str) -> None:
        proto_class = import_string(module)
        reg_fw_cmd.register(item, proto_class)

    @classmethod
    def load_command_proto(cls, cmd_proto: dict[int | RegFwCmd, str] | None = None) -> None:
        _cmd_proto: dict[int | RegFwCmd, str] = getattr(settings, 'COMMAND_PROTO', {}) or {}
        _cmd_proto.update(cmd_proto or {})
        reg_fw_cmd.clear()
        for k, v in _cmd_proto.items():
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
