"""Interface de comunicação com o modelo de linguagem."""

import requests

from ..config import config


def gerar_resposta(
    prompt: str,
    url: str | None = None,
    model: str | None = None,
    timeout: int | None = None,
) -> str:
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
        return dados.get("response", "[ERRO] Sem resposta do modelo").strip()
    except Exception as e:
        return f"[FALHA] {str(e)}"
