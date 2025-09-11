import json
import importlib.util
import sys
import types
from pathlib import Path
import unittest
from unittest.mock import patch

import tests.requests_stub  # noqa: F401
import tests.urllib3_stub  # noqa: F401
import tests.apscheduler_stub  # noqa: F401

hermes_pkg = types.ModuleType("hermes")
hermes_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "src/hermes")]
services_pkg = types.ModuleType("hermes.services")
services_pkg.__path__ = [
    str(Path(__file__).resolve().parents[1] / "src/hermes/services")
]
sys.modules.setdefault("hermes", hermes_pkg)
sys.modules.setdefault("hermes.services", services_pkg)

spec = importlib.util.spec_from_file_location(
    "hermes.services.llm_interface",
    Path(__file__).resolve().parents[1] / "src/hermes/services/llm_interface.py",
)
llm_interface = importlib.util.module_from_spec(spec)
sys.modules["hermes.services.llm_interface"] = llm_interface
spec.loader.exec_module(llm_interface)
gerar_resposta = llm_interface.gerar_resposta


def _make_response(payload: dict):
    import requests

    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode()
    return response


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

