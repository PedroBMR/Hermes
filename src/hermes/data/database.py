import sqlite3

from ..config import config
from .migrate import migrate_to_v2

# Allow tests to monkeypatch ``DB_PATH`` directly while defaulting to the
# value provided by :mod:`hermes.config`.
DB_PATH = config.DB_PATH

def inicializar_banco():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo TEXT NOT NULL,
                voz_id TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ideias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                source TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                llm_summary TEXT,
                llm_topic TEXT,
                tags TEXT,
                FOREIGN KEY(user_id) REFERENCES usuarios(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                trigger_at TEXT NOT NULL,
                triggered_at TEXT,
                FOREIGN KEY(user_id) REFERENCES usuarios(id)
            )
            """
        )

    migrate_to_v2(DB_PATH)

def criar_usuario(nome, tipo, voz_id=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, tipo, voz_id) VALUES (?, ?, ?)",
            (nome, tipo, voz_id),
        )

def buscar_usuarios():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, tipo FROM usuarios")
        return cursor.fetchall()

def salvar_ideia(
    user_id,
    title,
    body,
    source=None,
    llm_summary=None,
    llm_topic=None,
    tags=None,
):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ideias (
                user_id,
                title,
                body,
                source,
                llm_summary,
                llm_topic,
                tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, body, source, llm_summary, llm_topic, tags),
        )

def listar_ideias(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, body, created_at
            FROM ideias
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()
