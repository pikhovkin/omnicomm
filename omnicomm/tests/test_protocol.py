from unittest import TestCase

from omnicomm import commands, protocol


class ProtocolTest(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

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
            'num_rec': 0,
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
        data = protocol.ServerProtocol.pack(commands.Cmd86(value))
        cmd, remain = protocol.RegistrarProtocol.unpack(data)
        self.assertTrue(cmd.id == commands.Cmd86.id)
        self.assertTrue(cmd.value == value)
