import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hermes.core.registro_ideias import registrar_ideia_com_llm
from hermes.services import db


class TestRegistroIdeiasComBanco(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "registro.db"
        self.original_db_path = db.DB_PATH
        db.init_db(str(self.db_path))

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_registrar_popula_campos_do_llm(self):
        user_id = db.add_user("Usuaria", "humana")
        resposta_llm = """tema: Produtividade
resumo: Sistema de ideias
Tags: organizacao,rotina"""

        with patch(
            "hermes.core.registro_ideias.gerar_resposta",
            return_value={"ok": True, "response": resposta_llm},
        ), patch(
            "hermes.core.registro_ideias.PROMPT_PATH",
            Path(__file__).resolve().parents[1] / "prompts" / "resumo_classificar.md",
        ):
            retorno = registrar_ideia_com_llm(
                user_id,
                "Organizar",
                "Um sistema para registrar ideias",
                url="http://exemplo",
                model="teste-modelo",
            )

        ideias = db.list_ideas(user_id)
        self.assertEqual(len(ideias), 1)
        ideia = ideias[0]
        self.assertEqual(ideia["source"], "http://exemplo")
        self.assertEqual(ideia["llm_topic"], "Produtividade")
        self.assertEqual(ideia["llm_summary"], "Sistema de ideias")
        self.assertEqual(ideia["tags"], "organizacao,rotina")
        self.assertEqual(retorno, resposta_llm)


if __name__ == "__main__":
    unittest.main()
