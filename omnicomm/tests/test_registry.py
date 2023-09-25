from unittest import TestCase
from unittest.mock import Mock

from omnicomm.exceptions import ProtoDoesNotExistError
from omnicomm.registry import reg_fw_cmd


class ProtocolTest(TestCase):
    def test_register_unregister_command(self):
        reg_fw_cmd.register(42, Mock)
        self.assertTrue(reg_fw_cmd[42] is Mock)
        reg_fw_cmd.unregister(42)
        with self.assertRaises(ProtoDoesNotExistError):
            reg_fw_cmd[42]

    def test_clear_the_register(self):
        reg_fw_cmd.register(42, Mock)
        self.assertTrue(reg_fw_cmd._registry)
        reg_fw_cmd.clear()
        self.assertTrue(not reg_fw_cmd._registry)

    def test_a_command_registering(self):
        reg_fw_cmd.register(42, Mock)
        self.assertTrue(reg_fw_cmd[42] is Mock)
        reg_fw_cmd.register((0, 42), Mock)
        self.assertTrue(reg_fw_cmd[42] is Mock)
        reg_fw_cmd.register((0, 0, 42), Mock)
        self.assertTrue(reg_fw_cmd[42] is Mock)

        reg_fw_cmd.register((1, 42), Mock)
        self.assertTrue(reg_fw_cmd[(1, 42)] is Mock)
        reg_fw_cmd.register((0, 1, 42), Mock)
        self.assertTrue(reg_fw_cmd[(1, 42)] is Mock)

        reg_fw_cmd.register((1, 1, 42), Mock)
        self.assertTrue(reg_fw_cmd[(1, 1, 42)] is Mock)
