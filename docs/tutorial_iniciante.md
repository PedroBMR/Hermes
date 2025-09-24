# Tutorial para iniciantes: Hermes do zero à execução

Este guia explica, passo a passo, como preparar o computador, instalar e colocar o Hermes para funcionar. A proposta é falar com quem está começando agora: cada etapa está detalhada, com os comandos exatos e dicas para resolver os problemas mais comuns.

## 1. O que é o Hermes?

Hermes é um assistente pessoal privado que roda no seu computador. Ele permite registrar ideias, criar lembretes, conversar com um modelo de linguagem local e até ditar textos por voz. Tudo é armazenado localmente, com suporte a vários usuários e uma interface gráfica simples.

## 2. O que você vai instalar

Ao seguir este tutorial, você terá:

- O código-fonte do Hermes salvo no computador.
- Um ambiente Python com todas as bibliotecas necessárias.
- (Opcional) Reconhecimento de voz com o Vosk.
- (Opcional) Um servidor local de modelo de linguagem (LLM) usando o Ollama.
- Os atalhos para usar o Hermes pela linha de comando ou pela interface gráfica.

## 3. Pré-requisitos e preparação

### 3.1 Conhecimentos básicos

- Saber abrir o terminal (PowerShell no Windows ou Terminal no Linux).
- Saber navegar até uma pasta usando `cd nome_da_pasta`.
- Ter permissões de administrador quando o sistema pedir (especialmente no Windows).

### 3.2 Windows 10 ou superior

1. **Instale o Python 3.11 ou mais recente**:
   - Acesse <https://www.python.org/downloads/windows/>.
   - Baixe o instalador "Windows installer (64-bit)".
   - Execute o instalador e marque a opção **"Add Python to PATH"** antes de clicar em *Install Now*.
2. **Confirme que o Python e o `pip` funcionam** abrindo o PowerShell e rodando:
   ```powershell
   python --version
   pip --version
   ```
   Se o comando `python` não for reconhecido, tente `py --version`.
3. (Opcional) **Instale o Git** em <https://git-scm.com/download/win>. Ele facilita baixar atualizações do Hermes.

### 3.3 Linux (Ubuntu, Debian ou derivados)

1. Atualize os pacotes do sistema e instale o Python 3.11, `pip`, módulo de ambientes virtuais e o Git:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3-pip git
   ```
   Em distribuições que já trazem Python 3.11 por padrão, apenas confirme com `python3 --version`.
2. Certifique-se de que o comando `python3` aponta para a versão 3.11 ou superior. Se necessário, use `python3.11` diretamente nos comandos deste tutorial.

> 💡 **Dica:** reserve pelo menos 3 GB livres em disco. O modelo de voz e os modelos do Ollama podem ocupar mais espaço conforme você instala versões maiores.

## 4. Obter o código do Hermes

Escolha uma das opções:

- **Download manual (mais fácil):**
  1. Acesse a página do projeto no GitHub.
  2. Clique em **Code → Download ZIP**.
  3. Extraia o arquivo `.zip` em uma pasta fácil, por exemplo `Documentos/Hermes`.

- **Clonar com Git (recebe atualizações com mais facilidade):**
  ```bash
  git clone https://github.com/seu-usuario/Hermes.git
  cd Hermes
  ```
  Substitua `seu-usuario` pelo endereço correto do repositório.

## 5. Criar e ativar o ambiente virtual

Um ambiente virtual mantém as bibliotecas do Hermes separadas do restante do sistema.

1. Abra o terminal e entre na pasta onde o código foi salvo:
   ```bash
   cd caminho/para/Hermes
   ```
2. Crie o ambiente virtual:
   ```bash
   python -m venv .venv
   ```
   - No Windows, use `python` ou `py`.
   - No Linux, use `python3` ou `python3.11`, se necessário.
3. Ative o ambiente:
   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
     Se o PowerShell bloquear a execução, rode `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` uma única vez e tente novamente.
   - **Windows (Prompt de Comando):**
     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   - **Linux/macOS:**
     ```bash
     source .venv/bin/activate
     ```
4. Atualize o `pip` dentro do ambiente virtual (opcional, mas recomendado):
   ```bash
   pip install --upgrade pip
   ```

Sempre que for trabalhar no Hermes, lembre-se de ativar o ambiente virtual antes de rodar outros comandos.

## 6. Instalar o Hermes e as dependências principais

Com o ambiente virtual ativo e dentro da pasta do projeto, execute:

```bash
pip install -e .
```

Esse comando instala o Hermes em modo editável e baixa todas as bibliotecas obrigatórias (como PyQt5, requests e APScheduler). Caso prefira instalar apenas as dependências listadas, use `pip install -r requirements.txt`, mas para executar o Hermes como módulo o modo editável é o caminho mais simples.

## 7. Recursos opcionais

### 7.1 Entrada por voz com Vosk

1. Instale a biblioteca Python:
   ```bash
   pip install vosk
   ```
2. Baixe o modelo pequeno de voz em português brasileiro em <https://alphacephei.com/vosk/models> (procure por `vosk-model-small-pt-0.3.zip`).
3. Extraia o arquivo e mova a pasta resultante para `~/.cache/vosk/vosk-model-small-pt-0.3`:
   - Windows: `C:\Users\SEU_USUARIO\AppData\Local\vosk\vosk-model-small-pt-0.3`.
   - Linux: `/home/SEU_USUARIO/.cache/vosk/vosk-model-small-pt-0.3`.
4. Reinicie o Hermes caso ele já esteja aberto. Os botões de microfone na interface usarão o modelo baixado.

### 7.2 Modelo de linguagem com Ollama

O Hermes espera que um servidor LLM esteja disponível em `http://localhost:11434`. A maneira mais simples de conseguir isso é usando o Ollama.

1. **Instale o Ollama:**
   - Windows: instale usando o [instalador oficial](https://ollama.com/download) ou pelo comando `winget install Ollama.Ollama`.
   - Linux: siga as instruções da página oficial (por exemplo, no Ubuntu `curl -fsSL https://ollama.com/install.sh | sh`).
2. Abra um terminal separado e inicie o servidor:
   ```bash
   ollama serve
   ```
   Deixe essa janela aberta; o Ollama precisa continuar rodando para responder às solicitações do Hermes.
3. Em outra janela, baixe o modelo padrão esperado pelo Hermes:
   ```bash
   ollama pull mistral
   ```
   Você pode testar o modelo com `ollama run mistral "Olá, quem é você?"`.
4. Se desejar usar outro modelo ou alterar a porta padrão, ajuste as variáveis de ambiente antes de iniciar o Hermes. Exemplos:
   - Mudar o modelo padrão: `export HERMES_OLLAMA_MODEL=llama3` (Linux) ou `set HERMES_OLLAMA_MODEL=llama3` (PowerShell).
   - Mudar o endereço do servidor: `export HERMES_OLLAMA_URL=http://localhost:12345`.

## 8. Primeiro contato com o Hermes

### 8.1 Banco de dados

Na primeira execução, o Hermes cria automaticamente um arquivo `hermes.db` na pasta atual (ou no caminho indicado por `HERMES_DB_PATH`). É nele que ficam os usuários, ideias e lembretes.

### 8.2 Interface em linha de comando (CLI)

1. Certifique-se de que o Ollama está em execução se quiser receber sugestões do modelo de linguagem.
2. Com o ambiente virtual ativo, rode:
   ```bash
   python -m hermes.ui.cli
   ```
3. Siga as instruções exibidas no terminal:
   - Na primeira vez, será pedido que você cadastre um usuário.
   - O menu principal permite registrar ideias, listar e pesquisar ideias, criar lembretes e alternar de usuário.
   - Quando registrar uma nova ideia, o Hermes tentará obter sugestões do LLM. Se o servidor não estiver disponível, você pode salvar a ideia mesmo assim.

### 8.3 Interface gráfica (PyQt5)

1. Mantenha o Ollama rodando para habilitar as sugestões do modelo.
2. Execute:
   ```bash
   python -m hermes
   ```
3. A janela principal exibe os campos de título e descrição da ideia. Os botões com o ícone de microfone permitem ditar o texto (desde que o Vosk esteja instalado e configurado).
4. Ao salvar uma ideia com sucesso, o Hermes fala "ideia salva" como confirmação. Você pode navegar entre usuários e ideias a partir dos menus da janela.

## 9. API web opcional

Se quiser expor os recursos do Hermes via HTTP (por exemplo, para integrar com outros aplicativos), execute:

```bash
python -m hermes.api
```

- O serviço usa FastAPI e escuta na porta `8000` por padrão.
- O endpoint de verificação de saúde responde em `http://localhost:8000/health` com `{ "status": "ok" }`.
- Para proteger os demais endpoints, defina a variável `HERMES_API_TOKEN` antes de iniciar o serviço e envie o header `X-Token` com o mesmo valor ao fazer requisições.

Para executar continuamente no Linux, você pode instalar o serviço systemd fornecido em `packaging/linux`, conforme descrito na seção 11.

## 10. Configurações importantes

Os parâmetros mais usados podem ser definidos por variáveis de ambiente ou argumentos de linha de comando:

| O que altera                         | Variável                  | Argumento CLI       | Valor padrão                |
|-------------------------------------|---------------------------|---------------------|-----------------------------|
| Caminho do banco de dados           | `HERMES_DB_PATH`          | `--db-path`         | `hermes.db`                 |
| Porta sugerida para o servidor LLM* | `HERMES_API_PORT`         | `--api-port`        | `11434`                     |
| Modelo utilizado no Ollama          | `HERMES_OLLAMA_MODEL`     | `--ollama-model`    | `mistral`                   |
| URL do servidor Ollama              | `HERMES_OLLAMA_URL`       | `--ollama-url`      | `http://localhost:11434`    |
| Tempo limite das requisições (seg.) | `HERMES_TIMEOUT`          | `--timeout`         | `30`                        |

\* A variável `HERMES_API_PORT` existe por compatibilidade, mas para alterar de fato o endereço utilizado pelo Hermes prefira ajustar `HERMES_OLLAMA_URL` (ou usar o argumento `--ollama-url`).

Passe os argumentos ao executar `python -m hermes` ou `python -m hermes.ui.cli`. Em scripts shell, exporte as variáveis antes de iniciar a aplicação.

## 11. Opções avançadas

### 11.1 Criar executáveis no Windows

1. Instale o PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Rode o script de empacotamento:
   ```powershell
   packaging\windows\build.bat
   ```
3. Os executáveis `hermes.exe` (interface gráfica) e `hermes_api.exe` (API) ficarão em `dist\hermes`. Copie a pasta para outro computador se quiser.

### 11.2 Rodar como serviço no Linux

1. Copie o código do Hermes para `/opt/hermes` (ou ajuste o caminho `WorkingDirectory` em `packaging/linux/hermes.service`).
2. Instale o serviço systemd com privilégios de administrador:
   ```bash
   sudo ./packaging/linux/install.sh
   ```
3. Após a instalação, confirme que o serviço está ativo com `systemctl status hermes` e teste `curl localhost:8000/health`.

## 12. Solução de problemas

| Sintoma | Como resolver |
|---------|----------------|
| `python` não é reconhecido no Windows | Reabra o PowerShell, ou use `py` em vez de `python`. Se necessário, reinstale o Python marcando "Add Python to PATH". |
| `ModuleNotFoundError: No module named 'PyQt5'` | Verifique se o ambiente virtual está ativo e rode `pip install -e .` novamente. |
| O Ollama diz que a porta 11434 já está em uso | Feche outros programas que usem a porta ou inicie o Ollama com `ollama serve --port 12345` e defina `HERMES_OLLAMA_URL=http://localhost:12345`. |
| O Hermes não recebe respostas do modelo | Confirme se `ollama serve` está em execução e se o modelo foi baixado (`ollama pull mistral`). Verifique a conexão com `curl http://localhost:11434/api/generate`. |
| Botão de microfone não funciona | Confirme se o `vosk` está instalado, se o modelo foi extraído para a pasta correta e se o microfone está liberado pelo sistema. |

## 13. Próximos passos

- Explore a busca semântica: `python -m hermes.ui.cli` → opção **Pesquisar ideias**.
- Integre com outros sistemas via API (`python -m hermes.api`).
- Automatize backups do arquivo `hermes.db` para não perder suas ideias.

Com isso, o Hermes estará pronto para uso diário, mesmo que você esteja começando agora no mundo do desenvolvimento.
