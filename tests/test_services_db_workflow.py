import tempfile
import unittest
from pathlib import Path

from hermes.services import db


class TestServicesDBWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "services.db"
        self.original_db_path = db.DB_PATH
        db.init_db(str(self.db_path))

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_full_idea_crud_flow(self):
        user_id = db.add_user("Alice", "human", voice_id="voice-1")
        idea_one = db.add_idea(user_id, "Primeira", "Descricao 1", source="cli")
        idea_two = db.add_idea(user_id, "Segunda", "Descricao 2")

        users = db.list_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["id"], user_id)

        ideas = db.list_ideas(user_id)
        self.assertEqual({idea["id"] for idea in ideas}, {idea_one, idea_two})

        db.update_idea(idea_one, title="Atualizada", tags="um,dois")
        updated_ideas = {idea["id"]: idea for idea in db.list_ideas(user_id)}
        self.assertEqual(updated_ideas[idea_one]["title"], "Atualizada")
        self.assertEqual(updated_ideas[idea_one]["tags"], "um,dois")

        db.delete_idea(idea_two)
        remaining = db.list_ideas(user_id)
        self.assertEqual([idea["id"] for idea in remaining], [idea_one])


if __name__ == "__main__":
    unittest.main()
