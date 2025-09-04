import os
import tempfile
import unittest

from hermes.data import database


class TestBancoWorkflow(unittest.TestCase):
    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.orig = database.DB_PATH
        database.DB_PATH = self.temp_path
        database.inicializar_banco()

    def tearDown(self):
        database.DB_PATH = self.orig
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_workflow(self):
        usuarios = database.buscar_usuarios()
        nomes = [u[1] for u in usuarios]
        if "Pedro" not in nomes:
            database.criar_usuario("Pedro", "Masculino")
        if "Isabella" not in nomes:
            database.criar_usuario("Isabella", "Feminino")

        usuarios = database.buscar_usuarios()
        nomes = [u[1] for u in usuarios]
        self.assertIn("Pedro", nomes)
        self.assertIn("Isabella", nomes)

        pedro_id = next(u[0] for u in usuarios if u[1] == "Pedro")
        database.salvar_ideia(pedro_id, "Criar versao web", "Detalhes")
        ideias = database.listar_ideias(pedro_id)
        self.assertEqual(len(ideias), 1)
        self.assertEqual(ideias[0][0], "Criar versao web")
        self.assertEqual(ideias[0][1], "Detalhes")


if __name__ == "__main__":
    unittest.main()
