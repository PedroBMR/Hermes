import logging
import sys
from datetime import datetime, timedelta

from ..config import load_from_args
from ..core.registro_ideias import registrar_ideia_com_llm
from ..logging import setup_logging
from ..services import semantic_search
from ..services.db import (
    add_idea,
    add_reminder,
    add_user,
    init_db,
    list_ideas,
    list_reminders,
    list_users,
)
from ..services.reminders import load_pending_reminders, start_scheduler

logger = logging.getLogger(__name__)


def escolher_usuario():
    usuarios = list_users()
    if not usuarios:
        logger.info("Nenhum usuário encontrado. Crie um agora.")
        nome = input("Nome do novo usuário: ")
        tipo = input("Tipo (Masculino/Feminino): ")
        add_user(nome, tipo)
        usuarios = list_users()

    logger.info("\nUsuários disponíveis:")
    for usuario in usuarios:
        logger.info("%s - %s (%s)", usuario["id"], usuario["name"], usuario["kind"])

    while True:
        try:
            escolha = int(input("Escolha um usuário pelo ID: "))
            if any(u["id"] == escolha for u in usuarios):
                return escolha
            else:
                logger.error("ID inválido.")
        except ValueError:
            logger.error("Digite um número válido.")


def _parse_time(expr: str) -> str:
    """Convert a user-provided time expression to ISO format."""
    expr = expr.strip()
    try:
        if expr.startswith("+"):
            qty, unit = expr[1:].split(maxsplit=1)
            amount = int(qty)
            unit = unit.lower()
            if unit.startswith("min"):
                delta = timedelta(minutes=amount)
            elif unit.startswith("hour") or unit.startswith("hora"):
                delta = timedelta(hours=amount)
            elif unit.startswith("day") or unit.startswith("dia"):
                delta = timedelta(days=amount)
            else:
                raise ValueError
            dt = datetime.utcnow() + delta
        else:
            dt = datetime.fromisoformat(expr)
    except Exception as exc:
        raise ValueError("formato de tempo inválido") from exc
    return dt.replace(microsecond=0).isoformat()


def menu_principal(usuario_id, nome_usuario):
    while True:
        logger.info("\n=== Hermes (Usuário: %s) ===", nome_usuario)
        logger.info("1. Registrar nova ideia")
        logger.info("2. Listar minhas ideias")
        logger.info("3. Pesquisar ideias")
        logger.info("4. Criar lembrete")
        logger.info("5. Listar meus lembretes")
        logger.info("6. Trocar de usuário")
        logger.info("7. Sair")
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
            termo = input("Texto de busca: ")
            resultados = semantic_search(termo, user_id=usuario_id)
            if resultados:
                logger.info("\nResultados da busca:")
                for ideia in resultados:
                    logger.info(
                        "[%s] %s - %s",
                        ideia["created_at"],
                        ideia["title"],
                        ideia["body"],
                    )
            else:
                logger.info("Nenhuma ideia encontrada.")
        elif opcao == "4":
            mensagem = input("Texto do lembrete: ")
            quando = input("Quando? (ex: +1 minute): ")
            try:
                trigger_at = _parse_time(quando)
            except ValueError:
                logger.error("Formato de tempo inválido.")
                continue
            add_reminder(usuario_id, mensagem, trigger_at)
            load_pending_reminders()
            logger.info("✅ Lembrete agendado para %s.", trigger_at)
        elif opcao == "5":
            lembretes = list_reminders(usuario_id)
            pendentes = [r for r in lembretes if r["triggered_at"] is None]
            disparados = [r for r in lembretes if r["triggered_at"] is not None]
            if pendentes:
                logger.info("\nLembretes pendentes:")
                for r in pendentes:
                    logger.info("[%s] %s", r["trigger_at"], r["message"])
            else:
                logger.info("Nenhum lembrete pendente.")
            if disparados:
                logger.info("\nLembretes disparados:")
                for r in disparados:
                    logger.info("[%s] %s", r["trigger_at"], r["message"])
            else:
                logger.info("Nenhum lembrete disparado.")
        elif opcao == "6":
            return True  # trocar de usuário
        elif opcao == "7":
            logger.info("Encerrando Hermes.")
            return False
        else:
            logger.error("Opção inválida.")


def main(argv: list[str] | None = None):
    setup_logging()
    load_from_args(argv)
    init_db()
    start_scheduler()
    while True:
        usuario_id = escolher_usuario()
        nome_usuario = next(
            (u["name"] for u in list_users() if u["id"] == usuario_id),
            "Desconhecido",
        )
        if not menu_principal(usuario_id, nome_usuario):
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
