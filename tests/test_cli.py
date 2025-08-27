import runpy
import sys
import unittest
from unittest.mock import patch

from Hermes import main as cli


class TestCLI(unittest.TestCase):
    def test_menu_principal_quit_returns_false(self):
        with patch("builtins.input", side_effect=["4"]):
            result = cli.menu_principal(1, "User")
        self.assertFalse(result)

    def test_main_exits_cleanly(self):
        inputs = iter(["1", "4"])
        with patch("Hermes.database.inicializar_banco"), \
             patch("Hermes.database.buscar_usuarios", return_value=[(1, "User", "M")]), \
             patch("builtins.input", lambda _: next(inputs)):
            sys.modules.pop("Hermes.main", None)
            with self.assertRaises(SystemExit) as cm:
                runpy.run_module("Hermes.main", run_name="__main__")
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
