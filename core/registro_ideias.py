import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import salvar_ideia
from llm_interface import gerar_resposta

def registrar_ideia_com_llm(usuario_id: int, titulo: str, descricao: str) -> None:
    """Enviar a ideia ao modelo de linguagem e salvá-la."""
    print(f"Registrando ideia: {titulo}")
    print("Enviando ideia ao modelo para sugestões...")

    prompt = f"""Analise a seguinte ideia:
Título: {titulo}
Descrição: {descricao}

1. Classifique um tema geral (ex: produtividade, tecnologia, pessoal).
2. Sugira uma versão mais clara e resumida da descrição.
Responda no formato:
Tema: <tema>
Resumo: <resumo>
"""

    resposta = gerar_resposta(prompt)
    print("Resposta do modelo:")
    print(resposta)

    salvar_ideia(usuario_id, f"{titulo}\n\n{descricao}")

if __name__ == "__main__":
    usuario_id = 1  # Pedro
    titulo = "Sistema de organização de ideias com inteligência"
    descricao = "Quero um sistema que entenda minhas ideias e me ajude a organizar automaticamente por categoria, prioridade e clareza."
    registrar_ideia_com_llm(usuario_id, titulo, descricao)
