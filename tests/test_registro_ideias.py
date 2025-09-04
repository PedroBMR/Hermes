import unittest
from unittest.mock import patch

from hermes.core.registro_ideias import registrar_ideia_com_llm


class TestRegistrarIdeiaComLLM(unittest.TestCase):
    def test_registra_ideia_usa_llm_e_salva(self):
        usuario_id = 1
        titulo = "Titulo"
        descricao = "Descricao"
        url = "http://mock"
        model = "fake-model"

        with (
            patch(
                "hermes.core.registro_ideias.gerar_resposta",
                return_value={"ok": True, "response": "Tema: X\nResumo: Y"},
            ) as mock_llm,
            patch("hermes.core.registro_ideias.salvar_ideia") as mock_salvar,
            patch("builtins.print"),
        ):
            resposta = registrar_ideia_com_llm(
                usuario_id, titulo, descricao, url=url, model=model
            )

        mock_llm.assert_called_once()
        prompt = mock_llm.call_args.args[0]
        self.assertIn(titulo, prompt)
        self.assertIn(descricao, prompt)
        self.assertEqual(mock_llm.call_args.kwargs["url"], url)
        self.assertEqual(mock_llm.call_args.kwargs["model"], model)

        mock_salvar.assert_called_once_with(usuario_id, f"{titulo}\n\n{descricao}")
        self.assertEqual(resposta, "Tema: X\nResumo: Y")

    def test_falha_llm_gera_excecao(self):
        usuario_id = 1
        titulo = "Titulo"
        descricao = "Descricao"

        with (
            patch(
                "hermes.core.registro_ideias.gerar_resposta",
                return_value={"ok": False, "message": "erro"},
            ) as mock_llm,
            patch("hermes.core.registro_ideias.salvar_ideia") as mock_salvar,
            patch("builtins.print"),
        ):
            with self.assertRaises(RuntimeError):
                registrar_ideia_com_llm(usuario_id, titulo, descricao)

        mock_llm.assert_called_once()
        mock_salvar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
