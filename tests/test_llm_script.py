import unittest
from unittest.mock import patch

import requests
import tests.requests_stub  # noqa: F401

from hermes.services.llm_interface import gerar_resposta
from tests.test_llm_interface import _make_response


class TestarLLM(unittest.TestCase):
    @patch("requests.adapters.HTTPAdapter.send")
    def test_gerar_resposta(self, mock_send):
        mock_send.return_value = _make_response(
            {"response": "IA é a simulação de inteligência humana por máquinas."}
        )

        resultado = gerar_resposta(
            "Explique brevemente o que é inteligência artificial.",
            url="http://fake", model="fake",
        )
        assert resultado["ok"] is True
        assert (
            resultado["response"]
            == "IA é a simulação de inteligência humana por máquinas."
        )


if __name__ == "__main__":
    unittest.main()

