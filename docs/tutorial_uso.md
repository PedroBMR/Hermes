# Tutorial de uso do Hermes: torne-se produtivo no dia a dia

Este guia assume que você já concluiu a instalação descrita no [tutorial para iniciantes](tutorial_iniciante.md). Aqui nos
concentraremos no uso cotidiano do Hermes: como registrar ideias, organizar informações, configurar lembretes e automatizar
fluxos com a API.

---

## 1. Checklist rápido antes de começar

Antes de abrir o Hermes, confirme estes pontos:

| Item                              | Como verificar |
|-----------------------------------|----------------|
| Ambiente virtual ativado          | No terminal, confirme se o prompt mostra ``(.venv)`` ou rode `source .venv/bin/activate` (Linux/macOS) / `.venv\Scripts\Activate.ps1` (Windows). |
| Banco de dados acessível          | Por padrão é criado `hermes.db` na pasta atual. Use `ls`/`dir` para confirmar. |
| Servidor LLM (opcional, mas útil) | Rode `ollama serve` em um terminal separado e garanta que `ollama pull mistral` já foi executado. |
| Reconhecimento de voz (opcional)  | Certifique-se de ter instalado `vosk` e colocado o modelo em `~/.cache/vosk/...` conforme o tutorial inicial. |

Se algo não estiver pronto, retorne ao tutorial de instalação ou faça os ajustes agora.

---

## 2. Escolha seu modo de interação

O Hermes oferece três formas principais de uso. A tabela abaixo ajuda a decidir por onde começar:

| Modo                 | Ideal para...                                                     | Como iniciar |
|----------------------|-------------------------------------------------------------------|--------------|
| **CLI (terminal)**   | Quem prefere teclado, precisa de lembretes ou usa servidores remotos. | `python -m hermes.ui.cli` |
| **Interface gráfica**| Quem trabalha visualmente, quer ditar ideias e exportar resultados. | `python -m hermes` |
| **API HTTP**         | Integrações com outras ferramentas e automações.                    | `python -m hermes.api` (defina `HERMES_API_TOKEN` antes) |

Você pode alternar entre os modos sempre que desejar; todos compartilham o mesmo banco de dados.

---

## 3. Usando a interface de linha de comando (CLI)

1. Ative o ambiente virtual e execute:

   ```bash
   python -m hermes.ui.cli
   ```

2. **Escolha ou crie um usuário.** Se for sua primeira vez, informe um nome e um tipo (por exemplo, ``Pessoal`` ou ``Trabalho``).
   O Hermes lembrará esses dados para as próximas sessões.

3. A tela principal mostra o menu abaixo:

   | Opção | O que faz                                                                 |
   |-------|---------------------------------------------------------------------------|
   | 1     | Registrar uma nova ideia e solicitar sugestões ao LLM.                   |
   | 2     | Listar suas ideias em ordem da mais recente para a mais antiga.          |
   | 3     | Pesquisar ideias usando busca semântica e por palavras-chave.           |
   | 4     | Criar um lembrete com data/hora absoluta ou relativa.                    |
   | 5     | Ver lembretes pendentes e já disparados.                                 |
   | 6     | Trocar de usuário sem fechar o aplicativo.                               |
   | 7     | Encerrar o Hermes.                                                       |

### 3.1 Registrar ideias com ou sem IA

1. Escolha a opção **1** e informe título e descrição.
2. O Hermes tenta analisar a ideia com o LLM configurado. Ao funcionar, você verá um resumo/tema sugerido.
3. Caso o LLM esteja indisponível, aparecerá um aviso. Digite `s` para salvar mesmo assim ou `Enter` para cancelar.
4. Ideias salvas aparecem na lista da opção 2. Elas ficam associadas ao usuário atual e guardam os campos `llm_summary`, `llm_topic`
e `tags` quando a IA responde.

> 💡 **Dica:** personalize temporariamente o modelo executando `python -m hermes.ui.cli --ollama-model llama3`. O ajuste vale
> apenas para a sessão atual.

### 3.2 Pesquisar e revisar ideias

- Opção **2**: imprime cada registro com data, título e descrição.
- Opção **3**: digite um termo (ex.: `planejamento`). O Hermes procura no título, corpo e resumo do LLM, retornando os resultados
  mais relevantes.
- Para buscas avançadas em scripts Python, use diretamente:

  ```python
  from hermes.services import semantic_search

  resultados = semantic_search("kanban", user_id=1)
  for ideia in resultados:
      print(ideia["title"], ideia.get("llm_topic"))
  ```

### 3.3 Criar lembretes que falam com você

1. Escolha a opção **4** e informe a mensagem.
2. Em "Quando?", use um dos formatos aceitos:
   - Relativo: `+10 minutes`, `+2 hours`, `+1 day` (português ou inglês: `+3 horas`).
   - Data ISO: `2024-08-20T18:30`.
3. O Hermes agenda o lembrete e confirma a data/hora exata.
4. Quando o horário chegar, uma voz sintetizada (via `pyttsx3`) anuncia o lembrete. Se o sintetizador falhar, o texto aparece nos
   logs do terminal.
5. Use a opção **5** para revisar pendências e o histórico de lembretes já disparados.

> 🛎️ **Importante:** deixe pelo menos uma interface do Hermes aberta (CLI ou GUI) para que o agendador permaneça ativo.

### 3.4 Trocar usuário e adaptar o ambiente

- Use a opção **6** para alternar rapidamente para outro usuário.
- Deseja guardar dados em outro arquivo? Rode o comando com `--db-path /caminho/para/outro.db`.
- Para apontar para um servidor LLM remoto, utilize `--ollama-url http://servidor:11434` e mantenha o token de acesso em
  `HERMES_API_TOKEN` se o endpoint exigir autenticação.

---

## 4. Usando a interface gráfica (GUI)

1. No terminal com o ambiente ativo, execute:

   ```bash
   python -m hermes
   ```

2. A janela principal exibe, de cima para baixo:
   - Seletor de **usuário** e botão **Novo Usuário** (para cadastrar rapidamente).
   - Campos de **Título** e **Descrição** com botões de microfone (`🎙️`) que gravam 5 segundos de áudio e preenchem o texto usando
     o modelo Vosk.
   - Botões **Salvar Ideia**, **Exportar** e **Processar com IA**.
   - Barra de busca com filtro por usuário, data inicial e final.
   - Lista de ideias salvas, mostrando a data e o título.

### 4.1 Registrar ideias pela GUI

1. Selecione o usuário (ou crie um novo).
2. Preencha título e descrição — digite normalmente ou clique no microfone para ditar.
3. Clique em **Salvar Ideia**. O Hermes tenta enviar o conteúdo ao LLM:
   - Em caso de sucesso, um pop-up mostra o texto sugerido e o aplicativo fala “ideia salva”.
   - Se ocorrer erro, escolha **Sim** no diálogo para salvar sem análise.
4. As ideias aparecem imediatamente na lista da direita.

### 4.2 Buscar, revisar e processar ideias existentes

- **Busca rápida:** digite palavras-chave no campo superior e clique em **Buscar**.
- **Filtros:** escolha um usuário específico ou limite o período usando `AAAA-MM-DD` nos campos de data.
- **Visualizar detalhes:** dê um duplo clique em qualquer item para abrir um resumo completo com data, título e descrição.
- **Processar com IA:** selecione uma ideia na lista e clique no botão correspondente. O Hermes atualiza os campos de resumo e
  assunto (`llm_summary`/`llm_topic`), úteis em buscas futuras.
- **Exportar:** selecione uma ou mais ideias, clique em **Exportar** e escolha CSV ou TXT. Os arquivos gerados contêm data, título e
  descrição.

> 📁 **Sugestão:** exporte ideias periodicamente para criar backups externos ou compartilhar com sua equipe.

### 4.3 Boas práticas na interface

- Ative o Ollama antes de clicar em **Processar com IA** para evitar mensagens de erro.
- Caso o microfone não funcione, confirme se o modelo Vosk está no caminho correto e se o dispositivo está liberado pelo sistema
  operacional.
- Use o campo de busca em branco e clique em **Buscar** para atualizar a lista com todas as ideias do filtro atual.

---

## 5. Lembretes e notificações na prática

- Lembretes são criados atualmente pela CLI (opção 4). A GUI compartilha o mesmo agendador — portanto, deixar a janela aberta é
  suficiente para receber avisos sonoros.
- Após criar um lembrete, você pode manter apenas a GUI aberta: o agendador roda em segundo plano e tocará o aviso quando chegar
  o horário.
- Caso precise ajustar o texto ou a data, exclua o lembrete (opção 5 → “disparados”) e crie um novo com as informações corretas.

---

## 6. Automatizando com a API HTTP

A API é útil para capturar ideias de outros aplicativos, enviar prompts ao LLM ou integrar o Hermes a automações pessoais.

1. Defina um token de acesso e inicie o serviço:

   ```bash
   export HERMES_API_TOKEN="segredo-super"   # PowerShell: $Env:HERMES_API_TOKEN = "segredo-super"
   python -m hermes.api
   ```

2. Verifique se o servidor está no ar:

   ```bash
   curl http://localhost:8000/health
   # {"status":"ok"}
   ```

3. **Criar uma ideia remotamente:**

   ```bash
   curl -X POST http://localhost:8000/ideas \
        -H "Content-Type: application/json" \
        -H "X-Token: segredo-super" \
        -H "X-Device-Id: mobile" \
        -d '{"user": 1, "title": "Reunião", "body": "Enviar ata até sexta"}'
   ```

   O retorno inclui o `id` e a `source` usada para rastrear a origem (`caduceu_<device>`).

4. **Perguntar algo ao LLM via HTTP:**

   ```bash
   curl -X POST http://localhost:8000/ask \
        -H "Content-Type: application/json" \
        -H "X-Token: segredo-super" \
        -d '{"prompt": "Sugira 3 melhorias para meu fluxo de estudos"}'
   ```

   Se o Ollama estiver indisponível, o endpoint retorna erro 502 com a mensagem correspondente.

5. A API aplica um limite de 60 requisições por minuto por endereço IP. Planeje suas integrações para permanecer abaixo desse valor
   ou distribua chamadas ao longo do tempo.

---

## 7. Rotina de manutenção e produtividade

- **Backups:** copie o arquivo `hermes.db` regularmente para evitar perda de dados.
- **Ambientes separados:** use `--db-path` para experimentar ideias sem afetar seu arquivo principal.
- **Logs:** as mensagens de operação ficam em `~/.local/state/hermes/logs` (Linux) ou `%APPDATA%\Hermes\logs` (Windows). Consulte-os
  ao investigar problemas.
- **Serviço em segundo plano:** no Linux, utilize `packaging/linux/install.sh` para manter a API ativa via `systemd`.
- **Atualizações de modelo:** ajuste `HERMES_OLLAMA_MODEL` quando quiser testar outra base do Ollama.

---

Com este tutorial, você tem um panorama completo para usar o Hermes diariamente, seja registrando ideias rapidamente, recebendo
sugestões inteligentes, organizando lembretes ou conectando o assistente a outras ferramentas.
