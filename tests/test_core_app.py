from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from hermes import config
from hermes.core import app
from hermes.services import db, reminders


class CoreAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_core_app.db")

        self.original_config_db_path = config.config.DB_PATH
        self.original_db_path = db.DB_PATH
        self.original_scheduler = reminders._scheduler

        config.config.DB_PATH = self.db_path
        db.DB_PATH = self.db_path
        reminders._scheduler = None

        app.inicializar()

    def tearDown(self) -> None:
        if reminders._scheduler is not None:
            reminders._scheduler.shutdown()
        reminders._scheduler = self.original_scheduler

        config.config.DB_PATH = self.original_config_db_path
        db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_criar_usuario_e_listar_usuarios(self) -> None:
        user_id = app.criar_usuario("Alice", "humano")

        usuarios = app.listar_usuarios()

        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0]["id"], user_id)
        self.assertEqual(usuarios[0]["name"], "Alice")
        self.assertEqual(usuarios[0]["kind"], "humano")

    def test_registrar_ideia_sem_llm(self) -> None:
        user_id = app.criar_usuario("Bob", "humano")

        resultado = app.registrar_ideia(user_id, "Titulo", "Descricao", usar_llm=False)

        self.assertIn("id", resultado)
        ideias = app.listar_ideias(user_id)

        self.assertEqual(len(ideias), 1)
        self.assertEqual(ideias[0]["title"], "Titulo")
        self.assertEqual(ideias[0]["body"], "Descricao")
        self.assertIsNone(ideias[0]["llm_summary"])
        self.assertIsNone(ideias[0]["llm_topic"])
        self.assertIsNone(ideias[0]["tags"])

    def test_registrar_ideia_com_llm(self) -> None:
        user_id = app.criar_usuario("Carol", "humano")

        llm_response = {
            "response": "Resposta gerada",
            "llm_summary": "Resumo",
            "llm_topic": "Topico",
            "tags": "tag1, tag2",
        }
        with mock.patch(
            "hermes.core.app.analisar_ideia_com_llm", return_value=llm_response
        ):
            resultado = app.registrar_ideia(
                user_id,
                "Titulo LLM",
                "Descricao LLM",
                usar_llm=True,
                url="https://exemplo.com",
                model="test-model",
            )

        self.assertEqual(resultado["llm_response"], llm_response["response"])
        self.assertEqual(resultado["llm_summary"], llm_response["llm_summary"])
        self.assertEqual(resultado["llm_topic"], llm_response["llm_topic"])
        self.assertEqual(resultado["tags"], llm_response["tags"])

        ideias = app.listar_ideias(user_id)

        self.assertEqual(len(ideias), 1)
        self.assertEqual(ideias[0]["source"], "https://exemplo.com")
        self.assertEqual(ideias[0]["llm_summary"], llm_response["llm_summary"])
        self.assertEqual(ideias[0]["llm_topic"], llm_response["llm_topic"])
        self.assertEqual(ideias[0]["tags"], llm_response["tags"])

    def test_criar_lembrete_chama_add_reminder(self) -> None:
        with (
            mock.patch("hermes.core.app.add_reminder", return_value=42) as mock_add,
            mock.patch("hermes.core.app.reminders.load_pending_reminders") as mock_load,
        ):
            reminder_id = app.criar_lembrete(1, "Lembrar de testar", "2024-01-01T00:00:00")

        self.assertEqual(reminder_id, 42)
        mock_add.assert_called_once_with(1, "Lembrar de testar", "2024-01-01T00:00:00")
        mock_load.assert_called_once()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
