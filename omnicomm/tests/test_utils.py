from unittest import TestCase

from omnicomm.utils import cast_command_proto


class UtilsTest(TestCase):
    def test_cast_command_proto(self):
        command_proto = cast_command_proto(
            {
                '123': 'path.to.proto',
                '(1, 23)': 'path.to.proto',
                '(1, 2, 3)': 'path.to.proto',
            }
        )
        self.assertTrue(command_proto[123])
        self.assertTrue(command_proto[(1, 23)])
        self.assertTrue(command_proto[(1, 2, 3)])
