from unittest import TestCase

from omnicomm.utils import cast_command_proto


class UtilsTest(TestCase):
    def test_cast_command_proto(self):
        command_proto = cast_command_proto(
            {
                '123': 'path.to.proto1',
                '(1, 23)': 'path.to.proto2',
                '(1, 2, 3)': 'path.to.proto3',
            }
        )
        self.assertTrue(command_proto[123] == 'path.to.proto1')
        self.assertTrue(command_proto[(1, 23)] == 'path.to.proto2')
        self.assertTrue(command_proto[(1, 2, 3)] == 'path.to.proto3')
