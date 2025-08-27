import sys
import types
import unittest
from unittest.mock import patch, Mock

# Provide a minimal 'requests' stub if the real library is unavailable.
if 'requests' not in sys.modules:
    requests_stub = types.ModuleType('requests')
    class ConnError(Exception):
        pass
    requests_stub.exceptions = types.SimpleNamespace(ConnectionError=ConnError)
    requests_stub.post = lambda *a, **k: None
    sys.modules['requests'] = requests_stub

from Hermes import llm_interface


class TestGerarResposta(unittest.TestCase):
    @patch('Hermes.llm_interface.requests.post')
    def test_resposta_sucesso(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"response": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = llm_interface.gerar_resposta(
            "Oi?", url="http://test", model="fake"
        )
        self.assertEqual(result, "ok")

    @patch('Hermes.llm_interface.requests.post')
    def test_falha_conexao(self, mock_post):
        mock_post.side_effect = llm_interface.requests.exceptions.ConnectionError("falha")
        result = llm_interface.gerar_resposta(
            "Oi?", url="http://test", model="fake"
        )
        self.assertTrue(result.startswith("[FALHA]"))

    @patch('Hermes.llm_interface.requests.post')
    def test_resposta_inesperada(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"foo": "bar"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = llm_interface.gerar_resposta(
            "Oi?", url="http://test", model="fake"
        )
        self.assertEqual(result, "[ERRO] Sem resposta do modelo")


if __name__ == '__main__':
    unittest.main()
