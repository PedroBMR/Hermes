"""Interface de comunicação com o modelo de linguagem."""

import os
import requests

def gerar_resposta(prompt: str, url: str | None = None, model: str | None = None) -> str:
    """Envia um *prompt* ao servidor LLM e retorna a resposta.

    Parameters
    ----------
    prompt: str
        Texto a ser enviado ao modelo.
    url: str | None, optional
        URL do endpoint de geração. Se não for informado, é lido da
        variável de ambiente ``LLM_URL`` ou utiliza ``http://localhost:11434/api/generate``.
    model: str | None, optional
        Nome do modelo a ser utilizado. Se não for informado, é lido da
        variável de ambiente ``LLM_MODEL`` ou utiliza ``mistral``.
    """

    url = url or os.getenv("LLM_URL", "http://localhost:11434/api/generate")
    model = model or os.getenv("LLM_MODEL", "mistral")

    try:
        response = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        dados = response.json()
        return dados.get("response", "[ERRO] Sem resposta do modelo").strip()
    except Exception as e:
        return f"[FALHA] {str(e)}"
