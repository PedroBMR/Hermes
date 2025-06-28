# Hermes – Assistente Pessoal Offline

Assistente pessoal modular, privado e offline com múltiplos usuários, interface visual, entrada por voz/texto e integração com LLM local.

## Instalação das dependências

Use o `pip` para instalar os pacotes listados em `requirements.txt`:

```bash
pip install -r requirements.txt
```

Isso instalará também a dependência `requests` utilizada pelo projeto.

## Servidor LLM

Para funcionalidades que usam o modelo de linguagem é necessário que um
servidor esteja ativo em `http://localhost:11434`. Uma opção é rodar
o [Ollama](https://github.com/jmorganca/ollama) localmente:

```bash
ollama serve
```

## Executando o CLI

O modo em linha de comando inicia o fluxo principal da aplicação:

```bash
python main.py
```

## Executando a interface gráfica

Para abrir a interface gráfica (PyQt5):

```bash
python gui_ideias.py
```

## Testes

Os testes automatizados utilizam o módulo `unittest` padrão do Python.
Execute todos eles com:

```bash
python -m unittest discover -s tests
```

