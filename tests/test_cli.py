import sys
import unittest
from unittest.mock import patch

from dockspawn import cli


class TestCliDefaults(unittest.TestCase):
    def test_down_defaults_to_default_name(self):
        with patch.object(sys, "argv", ["dockspawn", "down"]), patch("dockspawn.cli.cmd_down") as mock_down:
            cli.main()
        self.assertEqual(mock_down.call_args.args[0].name, "default")

    def test_stop_alias_defaults_to_default_name(self):
        with patch.object(sys, "argv", ["dockspawn", "stop"]), patch("dockspawn.cli.cmd_down") as mock_down:
            cli.main()
        self.assertEqual(mock_down.call_args.args[0].name, "default")

    def test_logs_defaults_to_default_name(self):
        with patch.object(sys, "argv", ["dockspawn", "logs"]), patch("dockspawn.cli.cmd_logs") as mock_logs:
            cli.main()
        self.assertEqual(mock_logs.call_args.args[0].name, "default")

    def test_up_defaults_to_default_name(self):
        with patch.object(sys, "argv", ["dockspawn", "up"]), patch("dockspawn.cli.cmd_up") as mock_up:
            cli.main()
        self.assertEqual(mock_up.call_args.args[0].name, "default")


if __name__ == "__main__":
    unittest.main()
