import os
import tempfile
import unittest

from hermes.services import db as dao


class TestDatabase(unittest.TestCase):
    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.orig_path = dao.DB_PATH
        dao.init_db(self.temp_path)

    def tearDown(self):
        dao.DB_PATH = self.orig_path
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_criar_usuario(self):
        dao.add_user("Bob", "Masculino")
        usuarios = dao.list_users()
        self.assertEqual(len(usuarios), 1)
        usuario = usuarios[0]
        self.assertEqual(usuario["name"], "Bob")
        self.assertEqual(usuario["kind"], "Masculino")

    def test_salvar_e_listar_ideias(self):
        user_id = dao.add_user("Carol", "Feminino")
        dao.add_idea(user_id, "Titulo", "Minha ideia")
        ideias = dao.list_ideas(user_id)
        self.assertEqual(len(ideias), 1)
        ideia = ideias[0]
        self.assertEqual(ideia["title"], "Titulo")
        self.assertEqual(ideia["body"], "Minha ideia")
        self.assertTrue(ideia["created_at"])


if __name__ == "__main__":
    unittest.main()
