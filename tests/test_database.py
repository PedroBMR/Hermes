import os
import tempfile
import unittest

from Hermes import database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.orig_path = database.DB_PATH
        database.DB_PATH = self.temp_path
        database.inicializar_banco()

    def tearDown(self):
        database.DB_PATH = self.orig_path
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_criar_usuario(self):
        database.criar_usuario("Bob", "Masculino")
        usuarios = database.buscar_usuarios()
        self.assertEqual(len(usuarios), 1)
        uid, nome, tipo = usuarios[0]
        self.assertEqual(nome, "Bob")
        self.assertEqual(tipo, "Masculino")

    def test_salvar_e_listar_ideias(self):
        database.criar_usuario("Carol", "Feminino")
        uid = database.buscar_usuarios()[0][0]
        database.salvar_ideia(uid, "Minha ideia")
        ideias = database.listar_ideias(uid)
        self.assertEqual(len(ideias), 1)
        texto, data = ideias[0]
        self.assertEqual(texto, "Minha ideia")
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
