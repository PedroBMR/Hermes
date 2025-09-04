import os
import tempfile
import unittest

from hermes.data import database


class TestarBanco(unittest.TestCase):
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

    def test_criar_usuario_e_salvar_ideia(self):
        # cria usuarios
        database.criar_usuario("Pedro", "Masculino")
        database.criar_usuario("Isabella", "Feminino")

        usuarios = database.buscar_usuarios()
        nomes = [u[1] for u in usuarios]
        assert "Pedro" in nomes
        assert "Isabella" in nomes

        usuario_id = next(uid for uid, nome, _ in usuarios if nome == "Pedro")
        texto_ideia = "Criar uma versão web do Hermes acessível pela rede local."
        database.salvar_ideia(usuario_id, texto_ideia)

        ideias = database.listar_ideias(usuario_id)
        assert len(ideias) == 1
        assert ideias[0][0] == texto_ideia


if __name__ == "__main__":
    unittest.main()
