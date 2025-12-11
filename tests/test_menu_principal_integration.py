import io
import unittest
from unittest.mock import patch

from hermes.ui import cli as main


class TestMenuPrincipalIntegration(unittest.TestCase):
    def test_registra_ideia_fluxo(self):
        inputs = iter(["1", "Titulo", "Descricao", "5"])
        with (
            patch.object(
                main.app,
                "registrar_ideia",
                return_value={"llm_response": "Tema: X\nResumo: Y"},
            ) as mock_registrar,
            patch("builtins.input", lambda _: next(inputs)),
            patch("sys.stdout", new_callable=io.StringIO) as fake_out,
        ):
            main.setup_logging()
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        mock_registrar.assert_called_once_with(1, "Titulo", "Descricao", usar_llm=True)
        saida = fake_out.getvalue()
        self.assertIn("Ideia registrada", saida)
        self.assertIn("Sugestões do modelo", saida)
        self.assertIn("Tema: X", saida)

    def test_registra_sem_llm_quando_indisponivel(self):
        inputs = iter(["1", "Titulo", "Descricao", "s", "5"])
        with (
            patch.object(
                main.app,
                "registrar_ideia",
                side_effect=[RuntimeError("falha"), {"id": 1}],
            ) as mock_registrar,
            patch("builtins.input", lambda _: next(inputs)),
            patch("sys.stdout", new_callable=io.StringIO) as fake_out,
        ):
            main.setup_logging()
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        self.assertEqual(
            mock_registrar.call_args_list,
            [
                ((1, "Titulo", "Descricao"), {"usar_llm": True}),
                ((1, "Titulo", "Descricao"), {"usar_llm": False}),
            ],
        )
        saida = fake_out.getvalue()
        self.assertIn("Ideia registrada sem sugestões", saida)

    def test_listar_ideias_fluxo(self):
        inputs = iter(["2", "5"])
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

    def test_pesquisar_ideias_fluxo(self):
        inputs = iter(["3", "busca", "5"])
        ideias = [
            {"title": "Titulo1", "body": "Texto1", "created_at": "2024-01-01"},
            {"title": "Titulo2", "body": "Texto2", "created_at": "2024-01-02"},
        ]
        with (
            patch.object(main, "semantic_search", return_value=ideias) as mock_search,
            patch("builtins.input", lambda _: next(inputs)),
            patch("sys.stdout", new_callable=io.StringIO) as fake_out,
        ):
            main.setup_logging()
            result = main.menu_principal(1, "User")

        self.assertFalse(result)
        mock_search.assert_called_once_with("busca", user_id=1)
        saida = fake_out.getvalue()
        self.assertIn("Resultados da busca", saida)
        self.assertIn("[2024-01-01] Titulo1 - Texto1", saida)


if __name__ == "__main__":
    unittest.main()
