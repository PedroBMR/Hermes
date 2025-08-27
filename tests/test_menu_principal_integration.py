import io
import unittest
from unittest.mock import patch

from Hermes import main


class TestMenuPrincipalIntegration(unittest.TestCase):
    def test_registra_ideia_fluxo(self):
        inputs = iter(["1", "Minha ideia", "4"])
        with patch.object(main, "salvar_ideia") as mock_salvar, \
             patch("builtins.input", lambda _: next(inputs)), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        mock_salvar.assert_called_once_with(1, "Minha ideia")
        saida = fake_out.getvalue()
        self.assertIn("Ideia registrada", saida)

    def test_listar_ideias_fluxo(self):
        inputs = iter(["2", "4"])
        ideias = [("Texto", "2024-01-01")]
        with patch.object(main, "listar_ideias", return_value=ideias), \
             patch("builtins.input", lambda _: next(inputs)), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        saida = fake_out.getvalue()
        self.assertIn("Minhas ideias", saida)
        self.assertIn("[2024-01-01] Texto", saida)


if __name__ == "__main__":
    unittest.main()
