"""Registro de ideias utilizando o modelo de linguagem."""

import logging
from pathlib import Path

from ..services.db import add_idea
from ..services.llm_interface import LLMError, gerar_resposta

logger = logging.getLogger(__name__)


# Caminho para o arquivo de prompt. Lido dinamicamente em cada execução
PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "resumo_classificar.md"


def carregar_prompt() -> str:
    """Carrega o template de prompt a partir de um arquivo.

    Caso o arquivo seja YAML e a biblioteca ``yaml`` esteja disponível, a
    chave ``template`` é utilizada. Caso contrário, o conteúdo é retornado
    como texto simples. A leitura ocorre a cada chamada para refletir
    alterações no arquivo.
    """

    texto = PROMPT_PATH.read_text(encoding="utf-8")
    if PROMPT_PATH.suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(texto)
            if isinstance(data, dict):
                return data.get("template", "")
            return str(data)
        except Exception:
            return texto
    return texto


def analisar_ideia_com_llm(
    titulo: str,
    descricao: str,
    url: str | None = None,
    model: str | None = None,
) -> dict:
    """Obtém sugestões do LLM sem persistir a ideia.

    Retorna um dicionário contendo a resposta bruta do modelo e os campos
    extraídos: ``llm_summary``, ``llm_topic`` e ``tags``.
    """

    template = carregar_prompt()
    prompt = template.format(titulo=titulo, descricao=descricao)

    try:
        resultado = gerar_resposta(prompt, url=url, model=model)
    except LLMError as exc:
        raise RuntimeError(str(exc)) from exc

    if not resultado.get("ok", True):
        raise RuntimeError(resultado.get("message", "Erro desconhecido"))

    resposta = resultado["response"]
    tema = None
    resumo = None
    tags = None
    for linha in resposta.splitlines():
        if linha.lower().startswith("tema:"):
            tema = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("resumo:"):
            resumo = linha.split(":", 1)[1].strip()
        elif linha.lower().startswith("tags:"):
            tags = linha.split(":", 1)[1].strip()

    return {
        "response": resposta,
        "llm_summary": resumo,
        "llm_topic": tema,
        "tags": tags,
    }


def registrar_ideia_com_llm(
    usuario_id: int,
    titulo: str,
    descricao: str,
    url: str | None = None,
    model: str | None = None,
) -> str:
    logger.info("Registrando ideia: %s", titulo)
    logger.info("Enviando ideia ao modelo para sugestões...")

    dados = analisar_ideia_com_llm(titulo, descricao, url=url, model=model)

    add_idea(
        usuario_id,
        titulo,
        descricao,
        source=url,
        llm_summary=dados["llm_summary"],
        llm_topic=dados["llm_topic"],
        tags=dados["tags"],
    )
    return dados["response"]


if __name__ == "__main__":
    usuario_id = 1  # Pedro
    titulo = "Sistema de organização de ideias com inteligência"
    descricao = "Quero um sistema que entenda minhas ideias e me ajude a organizar automaticamente por categoria, prioridade e clareza."
    registrar_ideia_com_llm(usuario_id, titulo, descricao)
