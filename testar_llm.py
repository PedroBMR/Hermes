import os

from .llm_interface import gerar_resposta

pergunta = "Explique brevemente o que é inteligência artificial."
resposta = gerar_resposta(
    pergunta,
    url=os.getenv("LLM_URL"),
    model=os.getenv("LLM_MODEL"),
)
print("Resposta do modelo:")
print(resposta)
