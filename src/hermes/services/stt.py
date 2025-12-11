"""Serviços relacionados a reconhecimento de fala."""

from __future__ import annotations

from typing import TYPE_CHECKING

import logging

import vosk

if TYPE_CHECKING:
    from vosk import Model

logger = logging.getLogger(__name__)

_VOSK_MODEL: Model | None = None


def get_vosk_model(model_path: str | None = None) -> Model:
    """Obtém uma instância compartilhada de ``vosk.Model``.

    Args:
        model_path: Caminho opcional para o modelo. Se não informado, usa
            ``lang="pt-br"`` para carregar o modelo padrão.

    Returns:
        Instância única de ``vosk.Model`` no processo.
    """

    global _VOSK_MODEL

    if _VOSK_MODEL is not None:
        return _VOSK_MODEL

    try:
        logger.info(
            "Carregando modelo Vosk %s",
            f"de '{model_path}'" if model_path else "usando lang='pt-br'",
        )
        if model_path:
            _VOSK_MODEL = vosk.Model(model_path)
        else:
            _VOSK_MODEL = vosk.Model(lang="pt-br")
    except Exception:
        logger.exception(
            "Falha ao carregar modelo Vosk%s",
            f" de '{model_path}'" if model_path else "",
        )
        raise

    return _VOSK_MODEL
