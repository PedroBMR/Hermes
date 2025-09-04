"""Interface de comunicação com o modelo de linguagem."""

import logging
from json import JSONDecodeError
from typing import Any, Dict

import requests

from ..config import config

logger = logging.getLogger(__name__)


def gerar_resposta(
    prompt: str,
    url: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
) -> Dict[str, Any]:
    """Envia um *prompt* ao servidor LLM e retorna a resposta.

    Parameters
    ----------
    prompt: str
        Texto a ser enviado ao modelo.
    url: str | None, optional
        URL do endpoint de geração. Se ``None``, utiliza ``localhost`` com a
        porta definida em :mod:`hermes.config`.
    model: str | None, optional
        Nome do modelo a ser utilizado. Se ``None``, utiliza o valor de
        :mod:`hermes.config`.
    timeout: int | None, optional
        Tempo máximo (em segundos) de espera pela resposta. Se ``None``, usa o
        valor de :mod:`hermes.config`.
    """

    url = url or f"http://localhost:{config.API_PORT}/api/generate"
    model = model or config.OLLAMA_MODEL
    timeout = timeout or config.TIMEOUT

    try:
        response = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        response.raise_for_status()
        dados = response.json()
        resposta = dados.get("response")
        if resposta is None:
            return {
                "ok": False,
                "error": "missing_response",
                "message": "Sem resposta do modelo",
            }
        return {"ok": True, "response": resposta.strip()}
    except requests.exceptions.RequestException as exc:
        logger.exception("Erro ao comunicar com o servidor LLM: %s", exc)
        return {
            "ok": False,
            "error": exc.__class__.__name__,
            "message": str(exc),
        }
    except JSONDecodeError as exc:
        logger.exception("Resposta inválida do servidor LLM: %s", exc)
        return {
            "ok": False,
            "error": "JSONDecodeError",
            "message": str(exc),
        }
