"""Módulos do assistente Hermes."""

from .engine import carregar_prompt_sistema, responder_mensagem, responder_sobre_ideias
from .state import ConversationState

__all__ = [
    "carregar_prompt_sistema",
    "ConversationState",
    "HotwordListener",
    "responder_mensagem",
    "responder_sobre_ideias",
]


def __getattr__(name):
    if name == "HotwordListener":
        from .voice import HotwordListener

        return HotwordListener
    raise AttributeError(name)
