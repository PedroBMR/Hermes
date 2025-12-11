from __future__ import annotations

"""Fachada de alto nível para operações principais do Hermes."""

import logging
from typing import Any

from ..services import reminders, semantic_search
from ..services.db import (
    add_idea,
    add_reminder,
    add_user,
    init_db,
    list_ideas,
    list_reminders,
    list_users,
    search_ideas,
    update_idea,
)
from ..services.llm_interface import LLMError, gerar_resposta
from .registro_ideias import analisar_ideia_com_llm

logger = logging.getLogger(__name__)


def inicializar(db_path: str | None = None) -> None:
    """Inicializa dependências centrais como banco de dados e scheduler."""

    init_db(db_path)
    reminders.start_scheduler()


def listar_usuarios() -> list[dict]:
    """Lista todos os usuários cadastrados."""

    return list_users()


def criar_usuario(nome: str, tipo: str, voz_id: str | None = None) -> int:
    """Cria um novo usuário."""

    return add_user(nome, tipo, voz_id)


def registrar_ideia(
    user_id: int,
    titulo: str,
    descricao: str,
    usar_llm: bool = False,
    *,
    source: str | None = None,
    url: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Registra uma ideia usando o LLM opcionalmente."""

    origem = source or url
    if usar_llm:
        dados = analisar_ideia_com_llm(titulo, descricao, url=url, model=model)
        idea_id = add_idea(
            user_id,
            titulo,
            descricao,
            source=origem,
            llm_summary=dados["llm_summary"],
            llm_topic=dados["llm_topic"],
            tags=dados["tags"],
        )
        return {
            "id": idea_id,
            "llm_response": dados["response"],
            "llm_summary": dados["llm_summary"],
            "llm_topic": dados["llm_topic"],
            "tags": dados["tags"],
        }

    idea_id = add_idea(user_id, titulo, descricao, source=origem)
    return {"id": idea_id}


def listar_ideias(user_id: int) -> list[dict]:
    """Retorna todas as ideias do usuário informado."""

    return list_ideas(user_id)


def buscar_ideias(
    user_id: int | None,
    *,
    texto: str | None = None,
    topico: str | None = None,
    tag: str | None = None,
) -> list[dict]:
    """Realiza buscas textuais por ideias."""

    if user_id is None:
        resultados: list[dict] = []
        for usuario in list_users():
            resultados.extend(
                search_ideas(usuario["id"], texto, topico=topico, tag=tag)
            )
        return sorted(resultados, key=lambda i: i["created_at"], reverse=True)

    return search_ideas(user_id, texto, topic=topico, tag=tag)


def buscar_ideias_semanticas(user_id: int, termo: str, limite: int = 10) -> list[dict]:
    """Busca ideias semânticas para o usuário informado."""

    return semantic_search.semantic_search(termo, user_id=user_id, limit=limite)


def processar_ideia(
    ideia_id: int,
    titulo: str,
    descricao: str,
    *,
    url: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Processa uma ideia existente com o LLM e atualiza seus dados."""

    dados = analisar_ideia_com_llm(titulo, descricao, url=url, model=model)
    update_idea(
        ideia_id,
        llm_summary=dados["llm_summary"],
        llm_topic=dados["llm_topic"],
        tags=dados["tags"],
    )
    return dados


def criar_lembrete(user_id: int, mensagem: str, quando: str) -> int:
    """Cria um lembrete e agenda sua execução."""

    reminder_id = add_reminder(user_id, mensagem, quando)
    reminders.load_pending_reminders()
    return reminder_id


def listar_lembretes(user_id: int, apenas_pendentes: bool = False) -> list[dict]:
    """Retorna lembretes do usuário."""

    return list_reminders(user_id, only_pending=apenas_pendentes)


def responder_prompt(prompt: str, *, url: str | None = None, model: str | None = None) -> dict:
    """Encaminha um prompt diretamente ao LLM."""

    try:
        resultado = gerar_resposta(prompt, url=url, model=model)
    except LLMError as exc:
        raise RuntimeError(str(exc)) from exc

    if not resultado.get("ok", True):
        raise RuntimeError(resultado.get("message", "Erro ao consultar LLM"))
    return resultado


__all__ = [
    "inicializar",
    "listar_usuarios",
    "criar_usuario",
    "registrar_ideia",
    "listar_ideias",
    "buscar_ideias",
    "buscar_ideias_semanticas",
    "processar_ideia",
    "criar_lembrete",
    "listar_lembretes",
    "responder_prompt",
]
