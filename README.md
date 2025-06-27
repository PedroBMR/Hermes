# Hermes – Assistente Pessoal Offline

Hermes é um assistente pessoal modular focado em privacidade e execução totalmente local. O projeto permite registrar ideias e notas para diferentes usuários, oferecendo uma interface de linha de comando e uma interface gráfica simples em PyQt5. A geração de texto é feita localmente por meio do `ollama`, sem envio de dados para a nuvem.

## Instalação

É recomendável utilizar um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências listadas em `requirements.txt`:

```bash
pip install -r requirements.txt
```

As bibliotecas principais são **Vosk** para reconhecimento de voz, **PyQt5** para a interface gráfica e **ollama** para interação com o LLM.

## Como usar via linha de comando

Execute `main.py` para abrir o menu interativo:

```bash
python main.py
```

No menu é possível:

- Registrar nova ideia
- Listar ideias já cadastradas
- Trocar de usuário
- Encerrar o programa

Os dados ficam armazenados no arquivo `hermes.db`.

## Executar a interface gráfica

Para abrir a versão GUI basta rodar:

```bash
python gui_ideias.py
```

A janela permite escolher o usuário, preencher título e descrição da ideia e visualizar a lista de ideias gravadas. Dando duplo clique em uma entrada é exibido o conteúdo completo.

## Estrutura

- `core/` – funções de lógica e integração com LLM
- `database.py` – acesso ao banco SQLite
- `gui_ideias.py` – interface gráfica
- `main.py` – CLI principal
- `requirements.txt` – dependências do projeto

Contribuições são bem-vindas!
