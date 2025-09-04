import unittest
from unittest.mock import Mock, patch

import tests.requests_stub  # noqa: F401

from hermes.services.llm_interface import gerar_resposta


class TestarLLM(unittest.TestCase):
    @patch("hermes.services.llm_interface.requests.post")
    def test_gerar_resposta(self, mock_post):
        mock_resp = Mock()
        mock_resp.json.return_value = {
            "response": "IA é a simulação de inteligência humana por máquinas."
        }
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        resultado = gerar_resposta(
            "Explique brevemente o que é inteligência artificial.",
            url="http://fake", model="fake"
        )
        assert resultado["ok"] is True
        assert resultado["response"] == \
            "IA é a simulação de inteligência humana por máquinas."


if __name__ == "__main__":
    unittest.main()
