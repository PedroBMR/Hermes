"""Registro de ideias utilizando o modelo de linguagem."""

import logging

from ..data.database import salvar_ideia
from ..services.llm_interface import gerar_resposta

logger = logging.getLogger(__name__)


def registrar_ideia_com_llm(
    usuario_id: int,
    titulo: str,
    descricao: str,
    url: str | None = None,
    model: str | None = None,
) -> str:
    logger.info("Registrando ideia: %s", titulo)
    logger.info("Enviando ideia ao modelo para sugestões...")

    prompt = f"""Analise a seguinte ideia:
Título: {titulo}
Descrição: {descricao}

1. Classifique um tema geral (ex: produtividade, tecnologia, pessoal).
2. Sugira uma versão mais clara e resumida da descrição.
Responda no formato:
Tema: <tema>
Resumo: <resumo>
"""

    resultado = gerar_resposta(prompt, url=url, model=model)
    if not resultado.get("ok", False):
        raise RuntimeError(resultado.get("message", "Erro desconhecido"))

    resposta = resultado["response"]
    tema = None
    resumo = None
    for linha in resposta.splitlines():
        if linha.lower().startswith("tema:"):
            tema = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("resumo:"):
            resumo = linha.split(":", 1)[1].strip()

    salvar_ideia(
        usuario_id,
        titulo,
        descricao,
        source=url,
        llm_summary=resumo,
        llm_topic=tema,
    )
    return resposta


if __name__ == "__main__":
    usuario_id = 1  # Pedro
    titulo = "Sistema de organização de ideias com inteligência"
    descricao = "Quero um sistema que entenda minhas ideias e me ajude a organizar automaticamente por categoria, prioridade e clareza."
    registrar_ideia_com_llm(usuario_id, titulo, descricao)
