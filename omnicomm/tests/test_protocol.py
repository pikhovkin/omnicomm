import time
from unittest import TestCase

from omnicomm import commands, exceptions, protocol


class ProtocolTest(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_unpack_empty_data(self):
        with self.assertRaises(exceptions.EmptyDataError):
            protocol.Protocol.unpack(b'')
        with self.assertRaises(exceptions.EmptyDataError):
            protocol.ServerProtocol.unpack(b'')
        with self.assertRaises(exceptions.EmptyDataError):
            protocol.RegistrarProtocol.unpack(b'')

    def test_80(self):
        value = {'reg_id': 202000013, 'firmware': 114}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        cmd, remain = protocol.ServerProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd80.id)
        self.assertTrue(cmd.value == value)

    def test_85(self):
        value = {'rec_id': 62311}
        data = protocol.ServerProtocol.pack(commands.Cmd85(value))
        cmd, remain = protocol.RegistrarProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd85.id)
        self.assertTrue(cmd.value == value)

    def test_86(self):
        value = {
            'rec_id': 0,
            'omnicomm_time': 0,
            'unix_time': commands.Cmd85.BASE_TIME,
            'priority': 0,
            'msgs': [
                {
                    'mID': [1],
                    'general': {
                        'Time': 135433134,
                        'FLG': 7,
                        'Mileage': 0,
                        'VImp': 0,
                        'TImp': 1000,
                        'Uboard': 124,
                        'SumAcc': 102,
                    },
                    'nav': {
                        'LAT': 557887999,
                        'LON': 375883499,
                        'GPSVel': 3,
                        'GPSDir': 264,
                        'GPSNSat': 8,
                        'GPSAlt': 2096,
                    },
                },
            ],
        }
        data = protocol.RegistrarProtocol.pack(commands.Cmd86(value))
        cmd, remain = protocol.ServerProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd86.id)
        self.assertTrue(cmd.value == value)

    def test_93_from_server(self):
        value = {}
        data = protocol.ServerProtocol.pack(commands.Cmd93(value))
        cmd, remain = protocol.RegistrarProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd93.id)
        self.assertTrue(cmd.value == value)

    def test_93_from_registrar(self):
        value = {}
        data = protocol.RegistrarProtocol.pack(commands.Cmd93(value))
        cmd, remain = protocol.ServerProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd93.id)
        self.assertTrue(cmd.value == value)

    def test_94_from_server(self):
        value = {'unix_time': int(time.time())}
        data = protocol.ServerProtocol.pack(commands.Cmd94(value))
        cmd, remain = protocol.RegistrarProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd94.id)
        self.assertTrue(cmd.value['unix_time'] == value['unix_time'])

    def test_94_from_registrar(self):
        value = {'unix_time': int(time.time())}
        data = protocol.RegistrarProtocol.pack(commands.Cmd94(value))
        cmd, remain = protocol.ServerProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd94.id)
        self.assertTrue(cmd.value['unix_time'] == value['unix_time'])

    def test_95(self):
        value = {
            'rec_id': 0,
            'omnicomm_time': 0,
            'unix_time': commands.Cmd95.BASE_TIME,
            'priority': 0,
            'msgs': [
                {
                    'mID': [1],
                    'general': {
                        'Time': 135433134,
                        'FLG': 7,
                        'Mileage': 0,
                        'VImp': 0,
                        'TImp': 1000,
                        'Uboard': 124,
                        'SumAcc': 102,
                    },
                    'nav': {
                        'LAT': 557887999,
                        'LON': 375883499,
                        'GPSVel': 3,
                        'GPSDir': 264,
                        'GPSNSat': 8,
                        'GPSAlt': 2096,
                    },
                },
            ],
        }
        data = protocol.RegistrarProtocol.pack(commands.Cmd95(value))
        cmd, remain = protocol.ServerProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd95.id)
        self.assertTrue(cmd.value == value)


class ProtocolUnpackMany(TestCase):
    def test_cmd1_no_remain(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        cmds, remain = protocol.ServerProtocol.unpack_many(data)
        self.assertTrue(len(cmds) == 1)
        self.assertTrue(remain == b'')

    def test_cmd1_broken_remain(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        original_remain = data[:-1]
        cmds, remain = protocol.ServerProtocol.unpack_many(data + original_remain)
        self.assertTrue(len(cmds) == 1)
        self.assertTrue(remain == original_remain)

    def test_cmd2_no_remain(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        original_cmds = [data, data]
        cmds, remain = protocol.ServerProtocol.unpack_many(b''.join(original_cmds))
        self.assertTrue(len(cmds) == len(original_cmds))
        self.assertTrue(remain == b'')

    def test_cmd2_broken_remain(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        original_cmds = [data, data]
        original_remain = data[:-1]
        cmds, remain = protocol.ServerProtocol.unpack_many(b''.join(original_cmds) + original_remain)
        self.assertTrue(len(cmds) == len(original_cmds))
        self.assertTrue(remain == original_remain)

    def test_empty_data_error(self):
        with self.assertRaises(exceptions.EmptyDataError):
            protocol.ServerProtocol.unpack_many(b'')

    def test_frame_marker_does_not_exist_error(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        with self.assertRaises(exceptions.FrameMarkerDoesNotExistError):
            protocol.ServerProtocol.unpack_many(data[1:])

    def test_unpacking_crc_error(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        with self.assertRaises(exceptions.UnpackingCRCError):
            protocol.ServerProtocol.unpack_many(data[:-1])

    def test_crc_does_not_match_error(self):
        value = {'reg_id': 1234567890, 'firmware': 1}
        data = protocol.RegistrarProtocol.pack(commands.Cmd80(value))
        data = data[:-1] + bytes.fromhex(hex(data[-1] - 1)[2:])
        with self.assertRaises(exceptions.CRCDoesNotMatchError):
            protocol.ServerProtocol.unpack_many(data)
