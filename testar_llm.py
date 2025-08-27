from .llm_interface import gerar_resposta

pergunta = "Explique brevemente o que é inteligência artificial."
resposta = gerar_resposta(pergunta)
print("Resposta do modelo:")
print(resposta)
