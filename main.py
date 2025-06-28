from database import inicializar_banco, buscar_usuarios, criar_usuario, salvar_ideia, listar_ideias
from core.registro_ideias import registrar_ideia_com_llm

def escolher_usuario() -> int:
    """Permitir seleção ou criação de um usuário."""
    usuarios = buscar_usuarios()
    if not usuarios:
        print("Nenhum usuário encontrado. Crie um agora.")
        nome = input("Nome do novo usuário: ")
        tipo = input("Tipo (Masculino/Feminino): ")
        criar_usuario(nome, tipo)
        usuarios = buscar_usuarios()

    print("\nUsuários disponíveis:")
    for uid, nome, tipo in usuarios:
        print(f"{uid} - {nome} ({tipo})")

    while True:
        try:
            escolha = int(input("Escolha um usuário pelo ID: "))
            if any(u[0] == escolha for u in usuarios):
                return escolha
            else:
                print("ID inválido.")
        except ValueError:
            print("Digite um número válido.")

def menu_principal(usuario_id: int, nome_usuario: str) -> bool:
    """Menu interativo principal."""
    while True:
        print(f"\n=== Hermes (Usuário: {nome_usuario}) ===")
        print("1. Registrar nova ideia")
        print("2. Listar minhas ideias")
        print("3. Trocar de usuário")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            texto = input("Digite sua ideia: ")
            salvar_ideia(usuario_id, texto)
            print("✅ Ideia registrada.")
        elif opcao == "2":
            ideias = listar_ideias(usuario_id)
            if ideias:
                print("\nMinhas ideias:")
                for texto, data in ideias:
                    print(f"[{data}] {texto}")
            else:
                print("Nenhuma ideia registrada.")
        elif opcao == "3":
            return True  # trocar de usuário
        elif opcao == "4":
            print("Encerrando Hermes.")
            exit()
        else:
            print("Opção inválida.")

def main() -> None:
    """Executar a aplicação Hermes."""
    inicializar_banco()
    while True:
        usuario_id = escolher_usuario()
        nome_usuario = next((u[1] for u in buscar_usuarios() if u[0] == usuario_id), "Desconhecido")
        if not menu_principal(usuario_id, nome_usuario):
            break

if __name__ == "__main__":
    main()
