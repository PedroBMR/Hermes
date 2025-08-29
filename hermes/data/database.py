import sqlite3
from datetime import datetime

from ..config import config

# Allow tests to monkeypatch ``DB_PATH`` directly while defaulting to the
# value provided by :mod:`hermes.config`.
DB_PATH = config.DB_PATH

def conectar():
    return sqlite3.connect(DB_PATH)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            voz_id TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            texto TEXT NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()

def criar_usuario(nome, tipo, voz_id=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, tipo, voz_id) VALUES (?, ?, ?)", (nome, tipo, voz_id))
    conn.commit()
    conn.close()

def buscar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, tipo FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

def salvar_ideia(usuario_id, texto):
    data = datetime.now().isoformat()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ideias (usuario_id, texto, data) VALUES (?, ?, ?)", (usuario_id, texto, data))
    conn.commit()
    conn.close()

def listar_ideias(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT texto, data FROM ideias WHERE usuario_id = ? ORDER BY data DESC", (usuario_id,))
    ideias = cursor.fetchall()
    conn.close()
    return ideias
