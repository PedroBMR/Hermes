"""Estruturas de estado para conversas do Hermes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConversationState:
    """Mantém o contexto curto de uma sessão de conversa."""

    user_id: int | None
    history: list[dict[str, str]] = field(default_factory=list)

