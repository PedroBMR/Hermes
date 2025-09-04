import logging
import sys

from ..config import load_from_args
from ..core.registro_ideias import registrar_ideia_com_llm
from ..data.database import buscar_usuarios, criar_usuario, inicializar_banco
from ..logging import setup_logging
from ..services.db import add_idea, list_ideas

logger = logging.getLogger(__name__)


def escolher_usuario():
    usuarios = buscar_usuarios()
    if not usuarios:
        logger.info("Nenhum usuário encontrado. Crie um agora.")
        nome = input("Nome do novo usuário: ")
        tipo = input("Tipo (Masculino/Feminino): ")
        criar_usuario(nome, tipo)
        usuarios = buscar_usuarios()

    logger.info("\nUsuários disponíveis:")
    for uid, nome, tipo in usuarios:
        logger.info("%s - %s (%s)", uid, nome, tipo)

    while True:
        try:
            escolha = int(input("Escolha um usuário pelo ID: "))
            if any(u[0] == escolha for u in usuarios):
                return escolha
            else:
                logger.error("ID inválido.")
        except ValueError:
            logger.error("Digite um número válido.")


def menu_principal(usuario_id, nome_usuario):
    while True:
        logger.info("\n=== Hermes (Usuário: %s) ===", nome_usuario)
        logger.info("1. Registrar nova ideia")
        logger.info("2. Listar minhas ideias")
        logger.info("3. Trocar de usuário")
        logger.info("4. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            titulo = input("Título da ideia: ")
            descricao = input("Descrição da ideia: ")
            try:
                sugestoes = registrar_ideia_com_llm(usuario_id, titulo, descricao)
                logger.info("✅ Ideia registrada.")
                logger.info("Sugestões do modelo:")
                logger.info("%s", sugestoes)
            except RuntimeError as e:
                logger.error("⚠️ %s", e)
                if (
                    input("Deseja salvar a ideia mesmo assim? (s/N): ").strip().lower()
                    == "s"
                ):
                    add_idea(usuario_id, titulo, descricao)
                    logger.info("✅ Ideia registrada sem sugestões.")
                else:
                    logger.info("❌ Ideia não registrada.")
        elif opcao == "2":
            ideias = list_ideas(usuario_id)
            if ideias:
                logger.info("\nMinhas ideias:")
                for ideia in ideias:
                    logger.info(
                        "[%s] %s - %s",
                        ideia["created_at"],
                        ideia["title"],
                        ideia["body"],
                    )
            else:
                logger.info("Nenhuma ideia registrada.")
        elif opcao == "3":
            return True  # trocar de usuário
        elif opcao == "4":
            logger.info("Encerrando Hermes.")
            return False
        else:
            logger.error("Opção inválida.")


def main(argv: list[str] | None = None):
    setup_logging()
    load_from_args(argv)
    inicializar_banco()
    while True:
        usuario_id = escolher_usuario()
        nome_usuario = next(
            (u[1] for u in buscar_usuarios() if u[0] == usuario_id), "Desconhecido"
        )
        if not menu_principal(usuario_id, nome_usuario):
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
