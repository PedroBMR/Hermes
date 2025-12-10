"""Interface de comunicação com o modelo de linguagem."""

import logging
from json import JSONDecodeError
from typing import Any, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config import config

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    """Erro de comunicação com o modelo de linguagem."""

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        self.code = code


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
        URL do endpoint de geração. Se ``None``, utiliza
        :data:`hermes.config.config.OLLAMA_URL`.
    model: str | None, optional
        Nome do modelo a ser utilizado. Se ``None``, utiliza o valor de
        :mod:`hermes.config`.
    timeout: int | None, optional
        Tempo máximo (em segundos) de espera pela resposta. Se ``None``, usa o
        valor de :mod:`hermes.config`.
    """

    url = url or f"{config.OLLAMA_URL}/api/generate"
    model = model or config.OLLAMA_MODEL
    timeout = timeout or config.TIMEOUT

    session = requests.Session()
    retry = Retry(
        total=config.MAX_RETRIES,
        backoff_factor=config.BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=("POST",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    friendly_message = (
        "Não consegui falar com o modelo de linguagem. Verifique se o servidor"
        " está rodando em localhost:11434 e tente novamente."
    )

    try:
        response = session.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        response.raise_for_status()
        dados = response.json()
        resposta = dados.get("response")
        if resposta is None:
            raise LLMError("Sem resposta do modelo", code="missing_response")
        return {"ok": True, "response": resposta.strip()}
    except requests.exceptions.Timeout as exc:
        logger.exception("Servidor LLM não respondeu a tempo: %s", exc)
        raise LLMError(friendly_message, code="Timeout") from exc
    except requests.exceptions.ConnectionError as exc:
        logger.exception("Servidor LLM offline: %s", exc)
        raise LLMError(friendly_message, code="ConnectionError") from exc
    except requests.exceptions.RequestException as exc:
        logger.exception("Erro ao comunicar com o servidor LLM: %s", exc)
        raise LLMError(friendly_message, code=exc.__class__.__name__) from exc
    except JSONDecodeError as exc:
        logger.exception("Resposta inválida do servidor LLM: %s", exc)
        raise LLMError("Resposta inválida do servidor LLM", code="JSONDecodeError") from exc
    finally:
        session.close()
