# Hermes – Assistente Pessoal Offline

Assistente pessoal modular, privado e offline com múltiplos usuários, interface visual, entrada por voz/texto e integração com LLM local.

## Instalação

Instale o Hermes em modo editável para desenvolver ou executar localmente:

```bash
pip install -e .
```

Caso deseje instalar apenas as dependências listadas, utilize `requirements.txt`:

```bash
pip install -r requirements.txt
```

O arquivo de requisitos inclui o pacote `scikit-learn` (>=1.1),
necessário para a funcionalidade de busca semântica de ideias.

### Dependências opcionais

Algumas funcionalidades podem requerer bibliotecas adicionais que não
estão incluídas na instalação padrão:

- `vosk` – reconhecimento de fala. **Obrigatório** para utilizar a entrada
  por voz.
- `ollama` – cliente Python para o servidor Ollama.

Para usar voz, instale o `vosk` e baixe o modelo de linguagem [pt-BR pequeno](https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip).
Descompacte o conteúdo em `~/.cache/vosk/vosk-model-small-pt-0.3` para que o
aplicativo consiga localizar os arquivos offline.

Instale as dependências manualmente caso deseje experimentar esses recursos.

## Servidor LLM

Para funcionalidades que usam o modelo de linguagem é necessário que um
servidor esteja ativo em `http://localhost:11434`. Uma opção é rodar
o [Ollama](https://github.com/jmorganca/ollama) localmente:

```bash
ollama serve
```

### Configuração

Os principais parâmetros da aplicação podem ser ajustados via variáveis de
ambiente ou argumentos de linha de comando. Valores padrão:

| Parâmetro       | Variável de ambiente     | Argumento CLI     | Padrão                  |
|-----------------|--------------------------|-------------------|-------------------------|
| Caminho do banco| `HERMES_DB_PATH`         | `--db-path`       | `hermes.db`             |
| Porta do servidor LLM | `HERMES_API_PORT`   | `--api-port`      | `11434`                 |
| Modelo Ollama   | `HERMES_OLLAMA_MODEL`    | `--ollama-model`  | `mistral`               |
| Timeout (s)     | `HERMES_TIMEOUT`         | `--timeout`       | `30`                    |

O endpoint utilizado para comunicação com o LLM é construído a partir da
porta (`http://localhost:<porta>/api/generate`). Os argumentos de linha de
comando podem ser passados ao executar `python -m hermes` ou `python -m
hermes.ui.cli`.

Esses valores também podem ser informados diretamente ao chamar a função
`gerar_resposta`:

```python
from hermes.services.llm_interface import gerar_resposta
resposta = gerar_resposta("Oi?", url="http://meu-servidor:port/api/generate", model="outro-modelo")
```

## Execução

### CLI
O modo em linha de comando inicia o fluxo principal da aplicação:

```bash
python -m hermes.ui.cli
```

### Interface gráfica
Para abrir a interface gráfica (PyQt5):

```bash
python -m hermes
```

Na interface, os campos de título e descrição possuem um botão de microfone
("🎙️") que permite ditar texto. Ao salvar uma ideia com sucesso, o Hermes
fornece um breve feedback em voz dizendo "ideia salva".

### Pesquisa semântica
A aplicação oferece uma pesquisa de ideias baseada em similaridade
semântica. Após instalar as dependências, importe e utilize a função
`semantic_search`:

```python
from hermes.services.semantic_search import semantic_search

resultados = semantic_search("kanban", user_id=1)
for ideia in resultados:
    print(ideia["title"])
```

No modo CLI, selecione a opção **Pesquisar ideias** e informe o termo desejado.

O mecanismo utiliza por padrão um índice simples baseado em TF-IDF.  Para
substituí-lo por soluções mais avançadas como `FAISS` ou `Chroma`, implemente a
interface ``VectorIndex`` e forneça a instância ao chamar ``semantic_search``:

```python
from hermes.services.semantic_search import semantic_search, VectorIndex

class MeuIndice(VectorIndex):
    ...  # implemente fit() e search()

resultado = semantic_search("kanban", index=MeuIndice())
```

## Testes

Os testes automatizados utilizam o módulo `unittest` padrão do Python.
Execute todos eles com:

```bash
python -m unittest discover -s tests
```

## Desenvolvimento

Instale e configure os linters com [pre-commit](https://pre-commit.com/):

```bash
pip install pre-commit
pre-commit install
```

Consulte também [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo de contribuição,
[CHANGELOG.md](CHANGELOG.md) para o histórico de mudanças e
[LICENSE](LICENSE) para os termos de licença.

