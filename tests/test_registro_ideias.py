import unittest
from unittest.mock import patch

from Hermes.core.registro_ideias import registrar_ideia_com_llm


class TestRegistrarIdeiaComLLM(unittest.TestCase):
    def test_registra_ideia_usa_llm_e_salva(self):
        usuario_id = 1
        titulo = "Titulo"
        descricao = "Descricao"
        url = "http://mock"
        model = "fake-model"

        with patch("Hermes.core.registro_ideias.gerar_resposta", return_value="Tema: X\nResumo: Y") as mock_llm, \
             patch("Hermes.core.registro_ideias.salvar_ideia") as mock_salvar, \
             patch("builtins.print"):
            registrar_ideia_com_llm(usuario_id, titulo, descricao, url=url, model=model)

        mock_llm.assert_called_once()
        prompt = mock_llm.call_args.args[0]
        self.assertIn(titulo, prompt)
        self.assertIn(descricao, prompt)
        self.assertEqual(mock_llm.call_args.kwargs["url"], url)
        self.assertEqual(mock_llm.call_args.kwargs["model"], model)

        mock_salvar.assert_called_once_with(usuario_id, f"{titulo}\n\n{descricao}")


if __name__ == "__main__":
    unittest.main()
