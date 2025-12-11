"""Utilitários para carregar prompts do Hermes."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parents[3] / "prompts" / "assistant_system.md"
)

# Cache simples em memória para evitar leitura repetida do mesmo arquivo.
_SYSTEM_PROMPT_CACHE: str | None = None


def carregar_prompt_sistema() -> str:
    """Carrega o prompt de sistema do Hermes.

    Retorna o conteúdo do arquivo ``prompts/assistant_system.md``. Em caso de
    falha, registra uma mensagem de erro e retorna uma string vazia.
    """

    global _SYSTEM_PROMPT_CACHE

    if _SYSTEM_PROMPT_CACHE is not None:
        return _SYSTEM_PROMPT_CACHE

    try:
        _SYSTEM_PROMPT_CACHE = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error(
            "Arquivo de prompt do sistema não encontrado em %s", SYSTEM_PROMPT_PATH
        )
        _SYSTEM_PROMPT_CACHE = ""
    except OSError as exc:  # Abrange erros de leitura como permissões ou IO.
        logger.error(
            "Erro ao ler o prompt do sistema em %s: %s", SYSTEM_PROMPT_PATH, exc
        )
        _SYSTEM_PROMPT_CACHE = ""

    return _SYSTEM_PROMPT_CACHE
