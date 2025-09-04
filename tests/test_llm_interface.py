import unittest
from unittest.mock import Mock, patch

import tests.requests_stub  # noqa: F401

from hermes.services import llm_interface


class TestGerarResposta(unittest.TestCase):
    @patch("hermes.services.llm_interface.requests.post")
    def test_resposta_sucesso(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"response": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = llm_interface.gerar_resposta("Oi?", url="http://test", model="fake")
        self.assertTrue(result["ok"])  # type: ignore[index]
        self.assertEqual(result["response"], "ok")

    @patch("hermes.services.llm_interface.requests.post")
    def test_falha_conexao(self, mock_post):
        mock_post.side_effect = llm_interface.requests.exceptions.ConnectionError(
            "falha"
        )
        result = llm_interface.gerar_resposta("Oi?", url="http://test", model="fake")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "ConnectionError")

    @patch("hermes.services.llm_interface.requests.post")
    def test_resposta_inesperada(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"foo": "bar"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = llm_interface.gerar_resposta("Oi?", url="http://test", model="fake")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "missing_response")


if __name__ == "__main__":
    unittest.main()
