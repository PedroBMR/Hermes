# core/llm_controller.py

from llm_interface import send_to_llm

def gerar_resposta(prompt: str) -> str:
    """
    Recebe um prompt e retorna a resposta gerada pelo modelo LLM local.
    """
    try:
        resposta = send_to_llm(prompt)
        return resposta
    except Exception as e:
        return f"[ERRO] Falha ao obter resposta: {e}"
