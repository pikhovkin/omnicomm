from unittest import TestCase

from omnicomm import commands, protocol


class Cmd85Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex('67F30000')
        data = commands.Cmd85.unpack(msg)
        self.assertTrue(commands.Cmd85.pack(data) == msg)
        value = {'rec_id': 62311}
        data = commands.Cmd85.pack(value)
        self.assertTrue(commands.Cmd85.unpack(data) == value)


class Cmd86Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex('67f30000ae8b12080044000a01011308ae97ca4020072800300038e807407c50cc01142b08fec785940410d69bbce6021803208802280830e0202c330800100018e20220003443083810be10180444')
        data = commands.Cmd86.unpack(msg)
        self.assertTrue(commands.Cmd86.pack(data) == msg)
