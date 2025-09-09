import json
import unittest
from unittest.mock import patch

import requests
import tests.requests_stub  # noqa: F401

from hermes.services import llm_interface


def _make_response(payload: dict) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode()
    return response


class TestGerarResposta(unittest.TestCase):
    @patch("requests.adapters.HTTPAdapter.send")
    def test_resposta_sucesso(self, mock_send):
        mock_send.return_value = _make_response({"response": "ok"})

        with patch.object(llm_interface.config, "MAX_RETRIES", 1), patch.object(
            llm_interface.config, "BACKOFF_FACTOR", 0
        ):
            result = llm_interface.gerar_resposta(
                "Oi?", url="http://test", model="fake"
            )
        self.assertTrue(result["ok"])  # type: ignore[index]
        self.assertEqual(result["response"], "ok")

    @patch("requests.adapters.HTTPAdapter.send")
    def test_falha_conexao(self, mock_send):
        mock_send.side_effect = requests.exceptions.ConnectionError("falha")

        with patch.object(llm_interface.config, "MAX_RETRIES", 1), patch.object(
            llm_interface.config, "BACKOFF_FACTOR", 0
        ):
            result = llm_interface.gerar_resposta(
                "Oi?", url="http://test", model="fake"
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "ConnectionError")
        self.assertEqual(result["message"], "Servidor LLM offline")

    @patch("requests.adapters.HTTPAdapter.send")
    def test_timeout(self, mock_send):
        mock_send.side_effect = requests.exceptions.Timeout("timeout")

        with patch.object(llm_interface.config, "MAX_RETRIES", 1), patch.object(
            llm_interface.config, "BACKOFF_FACTOR", 0
        ):
            result = llm_interface.gerar_resposta(
                "Oi?", url="http://test", model="fake"
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "Timeout")
        self.assertEqual(result["message"], "Servidor LLM não respondeu a tempo")

    @patch("requests.adapters.HTTPAdapter.send")
    def test_resposta_inesperada(self, mock_send):
        mock_send.return_value = _make_response({"foo": "bar"})

        with patch.object(llm_interface.config, "MAX_RETRIES", 1), patch.object(
            llm_interface.config, "BACKOFF_FACTOR", 0
        ):
            result = llm_interface.gerar_resposta(
                "Oi?", url="http://test", model="fake"
            )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "missing_response")

    @patch("requests.Session.post")
    @patch("requests.Session.mount")
    def test_retry(self, mock_mount, mock_post):
        mock_post.return_value = _make_response({"response": "ok"})

        with patch.object(llm_interface.config, "MAX_RETRIES", 7), patch.object(
            llm_interface.config, "BACKOFF_FACTOR", 0.3
        ):
            result = llm_interface.gerar_resposta(
                "Oi?", url="http://test", model="fake"
            )
        self.assertTrue(result["ok"])  # type: ignore[index]
        adapter = mock_mount.call_args[0][1]
        self.assertEqual(adapter.max_retries.total, 7)
        self.assertEqual(adapter.max_retries.backoff_factor, 0.3)


if __name__ == "__main__":
    unittest.main()

