import os
import tempfile
import unittest

from hermes.services import db as dao


class TestBancoWorkflow(unittest.TestCase):
    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.orig = dao.DB_PATH
        dao.init_db(self.temp_path)

    def tearDown(self):
        dao.DB_PATH = self.orig
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_workflow(self):
        usuarios = dao.list_users()
        nomes = [u["name"] for u in usuarios]
        if "Pedro" not in nomes:
            dao.add_user("Pedro", "Masculino")
        if "Isabella" not in nomes:
            dao.add_user("Isabella", "Feminino")

        usuarios = dao.list_users()
        nomes = [u["name"] for u in usuarios]
        self.assertIn("Pedro", nomes)
        self.assertIn("Isabella", nomes)

        pedro_id = next(u["id"] for u in usuarios if u["name"] == "Pedro")
        dao.add_idea(pedro_id, "Criar versao web", "Detalhes")
        ideias = dao.list_ideas(pedro_id)
        self.assertEqual(len(ideias), 1)
        self.assertEqual(ideias[0]["title"], "Criar versao web")
        self.assertEqual(ideias[0]["body"], "Detalhes")


if __name__ == "__main__":
    unittest.main()
