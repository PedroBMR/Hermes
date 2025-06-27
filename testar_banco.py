from database import inicializar_banco, criar_usuario, buscar_usuarios, salvar_ideia, listar_ideias

# Inicializa banco e tabelas
inicializar_banco()

# Cria dois usuários (apenas se não existirem)
usuarios = buscar_usuarios()
nomes_existentes = [u[1] for u in usuarios]

if "Pedro" not in nomes_existentes:
    criar_usuario("Pedro", "Masculino")

if "Isabella" not in nomes_existentes:
    criar_usuario("Isabella", "Feminino")

# Mostra os usuários cadastrados
print("Usuários cadastrados:")
for uid, nome, tipo in buscar_usuarios():
    print(f"ID: {uid} | Nome: {nome} | Tipo: {tipo}")

# Seleciona o usuário Pedro e salva uma ideia
usuario_id = next((u[0] for u in buscar_usuarios() if u[1] == "Pedro"), None)
if usuario_id:
    salvar_ideia(usuario_id, "Criar uma versão web do Hermes acessível pela rede local.")

# Lista ideias do Pedro
print("\nIdeias do Pedro:")
for texto, data in listar_ideias(usuario_id):
    print(f"[{data}] {texto}")
