"""Legacy database helpers kept for backward compatibility.

This module delegates to :mod:`hermes.services.db` so that a single codepath
handles database access. New code should import from ``hermes.services.db``
instead.
"""

from ..config import config
from ..services import db as dao

# Allow tests to monkeypatch ``DB_PATH`` directly while defaulting to the
# value provided by :mod:`hermes.config`.
DB_PATH = config.DB_PATH


def _sync_db_path(db_path: str | None = None) -> str:
    """Ensure both modules share the same database path."""

    global DB_PATH
    if db_path:
        DB_PATH = db_path
    dao.DB_PATH = DB_PATH
    return DB_PATH


def inicializar_banco(db_path: str | None = None):
    """Initialize the database using the shared DAO implementation."""

    dao.init_db(_sync_db_path(db_path))


def criar_usuario(nome, tipo, voz_id=None):
    return dao.add_user(nome, tipo, voz_id)


def buscar_usuarios():
    return [(u["id"], u["name"], u["kind"]) for u in dao.list_users()]


def salvar_ideia(
    user_id,
    title,
    body,
    source=None,
    llm_summary=None,
    llm_topic=None,
    tags=None,
):
    return dao.add_idea(user_id, title, body, source, llm_summary, llm_topic, tags)


def listar_ideias(user_id):
    return [
        (i["title"], i["body"], i["created_at"])
        for i in dao.list_ideas(user_id)
    ]
