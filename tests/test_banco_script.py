import os
import tempfile
import unittest

from hermes.services import db as dao


class TestarBanco(unittest.TestCase):
    def setUp(self):
        fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.orig_path = dao.DB_PATH
        dao.init_db(self.temp_path)

    def tearDown(self):
        dao.DB_PATH = self.orig_path
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_criar_usuario_e_salvar_ideia(self):
        # cria usuarios
        dao.add_user("Pedro", "Masculino")
        dao.add_user("Isabella", "Feminino")

        usuarios = dao.list_users()
        nomes = [u["name"] for u in usuarios]
        assert "Pedro" in nomes
        assert "Isabella" in nomes

        usuario_id = next(u["id"] for u in usuarios if u["name"] == "Pedro")
        texto_ideia = "Criar uma versão web do Hermes acessível pela rede local."
        dao.add_idea(usuario_id, "Versao web", texto_ideia)

        ideias = dao.list_ideas(usuario_id)
        assert len(ideias) == 1
        assert ideias[0]["title"] == "Versao web"
        assert ideias[0]["body"] == texto_ideia


if __name__ == "__main__":
    unittest.main()
