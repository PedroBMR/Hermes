import io
import unittest
from unittest.mock import patch

from hermes.ui import cli as main


class TestMenuPrincipalIntegration(unittest.TestCase):
    def test_registra_ideia_fluxo(self):
        inputs = iter(["1", "Titulo", "Descricao", "4"])
        with (
            patch.object(
                main, "registrar_ideia_com_llm", return_value="Tema: X\nResumo: Y"
            ) as mock_registrar,
            patch("builtins.input", lambda _: next(inputs)),
            patch("sys.stdout", new_callable=io.StringIO) as fake_out,
        ):
            main.setup_logging()
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        mock_registrar.assert_called_once_with(1, "Titulo", "Descricao")
        saida = fake_out.getvalue()
        self.assertIn("Ideia registrada", saida)
        self.assertIn("Sugestões do modelo", saida)
        self.assertIn("Tema: X", saida)

    def test_registra_sem_llm_quando_indisponivel(self):
        inputs = iter(["1", "Titulo", "Descricao", "s", "4"])
        with (
            patch.object(
                main, "registrar_ideia_com_llm", side_effect=RuntimeError("falha")
            ),
            patch.object(main, "add_idea") as mock_add,
            patch("builtins.input", lambda _: next(inputs)),
            patch("sys.stdout", new_callable=io.StringIO) as fake_out,
        ):
            main.setup_logging()
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        mock_add.assert_called_once_with(1, "Titulo", "Descricao")
        saida = fake_out.getvalue()
        self.assertIn("Ideia registrada sem sugestões", saida)

    def test_listar_ideias_fluxo(self):
        inputs = iter(["2", "4"])
        ideias = [{"title": "Titulo", "body": "Texto", "created_at": "2024-01-01"}]
        with (
            patch.object(main, "list_ideas", return_value=ideias),
            patch("builtins.input", lambda _: next(inputs)),
            patch("sys.stdout", new_callable=io.StringIO) as fake_out,
        ):
            main.setup_logging()
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        saida = fake_out.getvalue()
        self.assertIn("Minhas ideias", saida)
        self.assertIn("[2024-01-01] Titulo - Texto", saida)


if __name__ == "__main__":
    unittest.main()
