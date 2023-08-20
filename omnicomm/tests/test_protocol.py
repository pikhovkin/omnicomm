from unittest import TestCase

from omnicomm import commands, protocol


class ProtocolTest(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_80(self):
        value = {'reg_id': 202000013, 'firmware': 114}
        data = protocol.RegisterProtocol.pack(commands.Cmd80, value)
        self.assertTrue(protocol.ServerProtocol.unpack(data)[0] == value)

    def test_85(self):
        value = {'rec_id': 62311}
        data = protocol.ServerProtocol.pack(commands.Cmd85, value)
        self.assertTrue(protocol.RegisterProtocol.unpack(data)[0] == value)
