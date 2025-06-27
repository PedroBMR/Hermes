# core/llm_controller.py

from llm_interface import gerar_resposta

# Preserve reference to the LLM helper before redefining
_gerar_resposta_llm = gerar_resposta

def gerar_resposta(prompt: str) -> str:
    """
    Recebe um prompt e retorna a resposta gerada pelo modelo LLM local.
    """
    try:
        resposta = _gerar_resposta_llm(prompt)
        return resposta
    except Exception as e:
        return f"[ERRO] Falha ao obter resposta: {e}"
