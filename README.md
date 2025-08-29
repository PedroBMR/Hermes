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

O endpoint e o modelo utilizados podem ser personalizados pelas variáveis
de ambiente:

- `LLM_URL` – URL do endpoint de geração (padrão:
  `http://localhost:11434/api/generate`)
- `LLM_MODEL` – nome do modelo a ser utilizado (padrão: `mistral`)

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

