"""Motor de respostas do assistente Hermes."""

from __future__ import annotations

import logging
import unicodedata
from typing import Iterable

from ..core import app
from ..core.prompts import carregar_prompt_sistema as _carregar_prompt_sistema
from ..services.llm_interface import LLMError, gerar_resposta
from .state import ConversationState

logger = logging.getLogger(__name__)

_MAX_HISTORICO = 10
_TERMOS_SOLICITACAO_EXTERNA = {
    "tempo la fora",
    "como está o tempo",
    "previsao do tempo",
    "previsão do tempo",
    "clima hoje",
    "noticias de hoje",
    "notícias de hoje",
    "quais as noticias",
    "quais as notícias",
}
_RESPOSTA_OFFLINE_PADRAO = (
    "Não tenho acesso ao mundo externo ou à internet. "
    "Posso, porém, te ajudar a planejar o dia com base nas suas ideias e tarefas."
)


def _normalizar_texto(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .lower()
    )


def _solicitacao_requer_mundo_externo(mensagem: str) -> bool:
    texto_normalizado = _normalizar_texto(mensagem)
    return any(termo in texto_normalizado for termo in _TERMOS_SOLICITACAO_EXTERNA)


def _deve_usar_contexto_ideias(mensagem: str) -> bool:
    termos_chave = {
        "ideia",
        "ideias",
        "projeto",
        "projetos",
        "plano",
        "planos",
        "prioridade",
        "prioridades",
        "organizacao de pensamentos",
        "organizar pensamentos",
        "organizar ideias",
    }

    texto_normalizado = _normalizar_texto(mensagem)
    return any(termo in texto_normalizado for termo in termos_chave)


def _registrar_no_historico(state: ConversationState | None, mensagem: str, resposta: str) -> None:
    if state is None:
        return

    state.history.append({"role": "user", "content": mensagem})
    state.history.append({"role": "assistant", "content": resposta})
    if len(state.history) > _MAX_HISTORICO:
        state.history[:] = state.history[-_MAX_HISTORICO :]


def carregar_prompt_sistema() -> str:
    """Retorna o prompt de sistema do Hermes.

    Wrapper simples em torno de :func:`hermes.core.prompts.carregar_prompt_sistema`
    para manter a API deste módulo.
    """

    return _carregar_prompt_sistema()


def coletar_contexto_ideias(user_id: int, pergunta: str) -> dict:
    """Recupera contexto de ideias relevantes para a pergunta do usuário.

    Usa busca semântica para trazer as ideias mais relacionadas e monta um
    texto de apoio a ser incluído no prompt enviado ao LLM.
    """

    if user_id is None:
        return {"contexto": "", "ideias": []}

    try:
        logger.info("Buscando ideias semânticas para o usuário %s", user_id)
        ideias = app.buscar_ideias_semanticas(user_id, pergunta, limite=5)
    except Exception:  # pragma: no cover - log e retorna contexto vazio
        logger.exception("Falha ao buscar ideias semânticas para o usuário %s", user_id)
        return {"contexto": "", "ideias": []}

    if not ideias:
        logger.info("Nenhuma ideia relacionada encontrada para o usuário %s", user_id)
        return {"contexto": "", "ideias": []}

    linhas: list[str] = []
    for ideia in ideias:
        titulo = ideia.get("title") or "(sem título)"
        resumo = ideia.get("llm_summary") or ideia.get("body") or "(sem resumo)"
        tags = ideia.get("tags") or "(sem tags)"
        criado_em = ideia.get("created_at") or "(data desconhecida)"
        linhas.append(
            f"- {titulo} ({criado_em}) | Tags: {tags} | Resumo: {resumo}"
        )

    contexto = (
        "Essas são algumas ideias que o usuário já registrou sobre temas "
        "possivelmente relacionados:\n" + "\n".join(linhas)
    )

    return {"contexto": contexto, "ideias": ideias}


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

    if _solicitacao_requer_mundo_externo(mensagem):
        _registrar_no_historico(state, mensagem, _RESPOSTA_OFFLINE_PADRAO)
        return _RESPOSTA_OFFLINE_PADRAO

    system_prompt = carregar_prompt_sistema()
    partes_prompt: list[str] = []

    if system_prompt:
        partes_prompt.append(system_prompt.strip())

    user_id = state.user_id if state else None
    if user_id is not None:
        partes_prompt.append(
            "Contexto: responda para o usuário identificado pelo id " f"{user_id}."
        )

        if _deve_usar_contexto_ideias(mensagem):
            logger.info("Incluindo contexto de ideias para o usuário %s", user_id)
            contexto_ideias = coletar_contexto_ideias(user_id, mensagem)
            if contexto_ideias.get("contexto"):
                partes_prompt.append(contexto_ideias["contexto"])
            else:
                logger.debug("Sem contexto de ideias para incluir no prompt")
        else:
            logger.info(
                "Contexto de ideias não incluído para o usuário %s (mensagem não pertinente)",
                user_id,
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

    _registrar_no_historico(state, mensagem, resposta_limpa)

    return resposta_limpa


def responder_sobre_ideias(
    pergunta: str, user_id: int, state: ConversationState | None
) -> str:
    """Responde a perguntas sobre ideias, planos e prioridades do usuário."""

    system_prompt = carregar_prompt_sistema()
    partes_prompt: list[str] = []

    if system_prompt:
        partes_prompt.append(system_prompt.strip())

    partes_prompt.append(
        "Contexto: responda para o usuário identificado pelo id " f"{user_id}."
    )

    contexto_ideias = coletar_contexto_ideias(user_id, pergunta)
    if contexto_ideias.get("contexto"):
        partes_prompt.append(contexto_ideias["contexto"])
    else:
        logger.debug("Sem contexto de ideias para incluir no prompt de ideação")

    historico = state.history if state else None
    if historico:
        historico_formatado = _formatar_historico(historico)
        if historico_formatado:
            partes_prompt.append(historico_formatado)

    partes_prompt.append(
        (
            "Tarefa: atue como consultor das ideias do usuário. "
            "Ofereça uma análise estruturada com pontos fortes e fracos, identifique riscos "
            "ou potenciais furos e sugira próximos passos claros. Referencie ideias e discussões "
            "anteriores sempre que possível para manter continuidade."
        )
    )
    partes_prompt.append(f"Usuário: {pergunta}")
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

    _registrar_no_historico(state, pergunta, resposta_limpa)

    return resposta_limpa
