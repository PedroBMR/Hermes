# Hermes – Assistente Pessoal Offline

Assistente pessoal modular, privado e offline com múltiplos usuários, interface visual, entrada por voz/texto e integração com LLM local.

## Instalação das dependências

Use o `pip` para instalar os pacotes listados em `requirements.txt`:

```bash
pip install -r requirements.txt
```

Isso instalará também a dependência `requests` utilizada pelo projeto.

### Dependências opcionais

Algumas funcionalidades futuras podem requerer bibliotecas adicionais que não
estão incluídas na instalação padrão:

- `vosk` – reconhecimento de fala.
- `ollama` – cliente Python para o servidor Ollama.

Instale-as manualmente caso deseje experimentar esses recursos.

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

## Executando o CLI

O modo em linha de comando inicia o fluxo principal da aplicação:

```bash
python -m hermes.ui.cli
```

## Executando a interface gráfica

Para abrir a interface gráfica (PyQt5):

```bash
python -m hermes
```

## Testes

Os testes automatizados utilizam o módulo `unittest` padrão do Python.
Execute todos eles com:

```bash
python -m unittest discover -s tests
```

