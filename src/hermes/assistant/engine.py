"""Motor de respostas do assistente Hermes."""

from __future__ import annotations

import logging
from typing import Iterable

from ..core.prompts import carregar_prompt_sistema as _carregar_prompt_sistema
from ..services.llm_interface import LLMError, gerar_resposta
from .state import ConversationState

logger = logging.getLogger(__name__)

_MAX_HISTORICO = 10


def carregar_prompt_sistema() -> str:
    """Retorna o prompt de sistema do Hermes.

    Wrapper simples em torno de :func:`hermes.core.prompts.carregar_prompt_sistema`
    para manter a API deste módulo.
    """

    return _carregar_prompt_sistema()


def _formatar_historico(historico: Iterable[dict]) -> str:
    partes: list[str] = []
    for entrada in historico:
        role = entrada.get("role", "usuario")
        conteudo = entrada.get("content") or entrada.get("mensagem") or ""
        prefixo = "Hermes" if role.lower() in {"assistant", "hermes"} else "Usuário"
        partes.append(f"- {prefixo}: {conteudo}")
    if not partes:
        return ""
    return "Histórico:\n" + "\n".join(partes)


def responder_mensagem(
    mensagem: str,
    state: ConversationState | None = None,
) -> str:
    """Recebe uma mensagem do usuário e retorna a resposta textual do Hermes."""

    system_prompt = carregar_prompt_sistema()
    partes_prompt: list[str] = []

    if system_prompt:
        partes_prompt.append(system_prompt.strip())

    user_id = state.user_id if state else None
    if user_id is not None:
        partes_prompt.append(
            "Contexto: responda para o usuário identificado pelo id " f"{user_id}."
        )

    historico = state.history if state else None
    if historico:
        historico_formatado = _formatar_historico(historico)
        if historico_formatado:
            partes_prompt.append(historico_formatado)

    partes_prompt.append(f"Usuário: {mensagem}")
    partes_prompt.append("Hermes:")

    prompt_completo = "\n\n".join(partes_prompt).strip()

    try:
        resultado = gerar_resposta(prompt_completo)
    except LLMError as exc:
        logger.exception("LLM offline ou indisponível: %s", exc)
        return (
            "Não consegui falar com o modelo de linguagem agora. "
            "Por favor, tente novamente em alguns instantes."
        )
    except Exception as exc:  # Cobertura para erros inesperados
        logger.exception("Erro inesperado ao gerar resposta: %s", exc)
        return (
            "Tive um problema inesperado ao gerar a resposta. "
            "Pode tentar de novo daqui a pouco?"
        )

    if not resultado.get("ok", True):
        logger.error("LLM retornou erro: %s", resultado)
        return (
            "O modelo de linguagem não conseguiu responder agora. "
            "Tente novamente em breve."
        )

    resposta = resultado.get("response", "")
    if not resposta:
        logger.warning("Resposta vazia recebida do LLM")
        return "Não recebi nenhuma resposta do modelo agora, pode tentar de novo?"

    resposta_limpa = resposta.strip()

    if state is not None:
        state.history.append({"role": "user", "content": mensagem})
        state.history.append({"role": "assistant", "content": resposta_limpa})
        if len(state.history) > _MAX_HISTORICO:
            state.history[:] = state.history[-_MAX_HISTORICO :]

    return resposta_limpa
