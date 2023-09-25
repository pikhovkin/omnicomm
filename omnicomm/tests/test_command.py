from unittest import TestCase

from omnicomm import commands, protocol


class Cmd85Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex('67F30000')
        cmd85 = commands.Cmd85.unpack(msg)
        self.assertTrue(commands.Cmd85(cmd85.value).pack() == msg)
        value = {'rec_id': 62311}
        data = commands.Cmd85(value).pack()
        self.assertTrue(commands.Cmd85.unpack(data).value == value)


class Cmd86Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex(
            '67f30000ae8b12080044000a01011308ae97ca4020072800300038e807407c50cc01142b08fec785940410d69bbce6021803208802280830e0202c330800100018e20220003443083810be10180444'  # noqa: E501
        )
        cmd86 = commands.Cmd86.unpack(msg)
        self.assertTrue(commands.Cmd86(cmd86.value).pack() == msg)


class Cmd93Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex('')
        cmd93 = commands.Cmd93.unpack(msg)
        self.assertTrue(commands.Cmd93(cmd93.value).pack() == msg)
        value = {}
        data = commands.Cmd93(value).pack()
        self.assertTrue(commands.Cmd93.unpack(data).value == value)


class Cmd94Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex('c4a6b51b')
        cmd94 = commands.Cmd94.unpack(msg)
        self.assertTrue(commands.Cmd94(cmd94.value).pack() == msg)
        value1 = {'omnicomm_time': 464889540}
        data = commands.Cmd94(value1).pack()
        self.assertTrue(commands.Cmd94.unpack(data).value['omnicomm_time'] == value1['omnicomm_time'])
        value2 = {'unix_time': 1695657540}
        data = commands.Cmd94(value2).pack()
        self.assertTrue(commands.Cmd94.unpack(data).value['omnicomm_time'] == value1['omnicomm_time'])


class Cmd95Test(TestCase):
    def setUp(self) -> None:
        protocol.Protocol.load_command_proto()

    def test_simple(self):
        msg = bytes.fromhex(
            '67f30000ae8b12080044000a01011308ae97ca4020072800300038e807407c50cc01142b08fec785940410d69bbce6021803208802280830e0202c330800100018e20220003443083810be10180444'  # noqa: E501
        )
        cmd95 = commands.Cmd95.unpack(msg)
        self.assertTrue(commands.Cmd86(cmd95.value).pack() == msg)
