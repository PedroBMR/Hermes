import runpy
import sys
import unittest
from unittest.mock import patch

from hermes.ui import cli


class TestCLI(unittest.TestCase):
    def test_menu_principal_quit_returns_false(self):
        with patch("builtins.input", side_effect=["4"]):
            result = cli.menu_principal(1, "User")
        self.assertFalse(result)

    def test_main_exits_cleanly(self):
        inputs = iter(["1", "4"])
        with patch("hermes.data.database.inicializar_banco"), \
             patch("hermes.data.database.buscar_usuarios", return_value=[(1, "User", "M")]), \
             patch("builtins.input", lambda _: next(inputs)):
            sys.modules.pop("hermes.ui.cli", None)
            with self.assertRaises(SystemExit) as cm:
                runpy.run_module("hermes.ui.cli", run_name="__main__")
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
