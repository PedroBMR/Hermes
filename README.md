# Hermes – Assistente Pessoal Offline

> ⏸️ **Status do projeto: Pausado.** O desenvolvimento está temporariamente parado (último commit em dez/2025), mas o projeto **será retomado no futuro**. Este README documenta o estado atual do código para facilitar a retomada.

Assistente pessoal modular, privado e offline com múltiplos usuários, interface visual, entrada por voz/texto e integração com LLM local.

> 📘 Precisa de um passo a passo para iniciantes? Confira o [tutorial completo](docs/tutorial_iniciante.md).

---

## 🎯 Visão do projeto

O Hermes é um assistente de IA pessoal que roda **inteiramente offline**, com foco em privacidade: nenhuma ideia, pergunta ou dado do usuário sai da máquina local. A proposta é permitir registrar ideias, tirar dúvidas e organizar informações por **voz ou texto**, com um LLM local respondendo e ajudando a estruturar o conteúdo, além de lembretes e busca semântica sobre o que já foi registrado.

Pontos centrais da visão:
- **Offline-first**: LLM local via Ollama, reconhecimento de voz local via Vosk, síntese de voz local via pyttsx3 — sem dependência de serviços em nuvem.
- **Privado**: os dados ficam em um banco local (SQLite); não há telemetria nem envio de dados para terceiros.
- **Multiusuário**: cada pessoa tem seu próprio espaço de ideias/lembretes no mesmo banco.
- **Multi-interface**: a mesma base de dados pode ser acessada via CLI, GUI (PyQt5) ou API HTTP (FastAPI) — inclusive por dispositivos remotos na rede local (ver cliente "Caduceu" abaixo).
- **Voz e texto**: captura de voz pontual ou por hotword (escuta contínua), com feedback falado nas ações principais.

## ✅ O que já foi implementado

- **Registro de ideias** com título, descrição e sugestões geradas pelo LLM local (Ollama, modelo padrão `mistral`).
- **Múltiplos usuários**, com troca de usuário sem fechar o app.
- **Interface gráfica (PyQt5)** completa, com botão de ditado por voz (🎙️) nos campos de título/descrição e feedback sonoro ao salvar.
- **CLI** com menu principal (registrar ideia, listar, pesquisar, criar/listar lembretes, trocar usuário).
- **API HTTP (FastAPI)**, com autenticação por token (`HERMES_API_TOKEN`), usada pelo cliente remoto.
- **Cliente remoto "Caduceu"** (`clients/caduceu`): cliente leve, estilo *push-to-talk*, que fala com um servidor Hermes via `POST /ideas` e `POST /ask`, identificando o dispositivo (ex.: `caduceu_cozinha`) — pensado para múltiplos pontos de captura na casa.
- **Busca semântica** de ideias baseada em TF-IDF (scikit-learn), com interface `VectorIndex` já preparada para trocar por FAISS/Chroma no futuro.
- **Lembretes** agendados via APScheduler, com tempo absoluto ou relativo (ex.: `+1 minute`).
- **Reconhecimento e síntese de voz offline**: Vosk (STT, modelo pt-BR) + pyttsx3 (TTS), com modo de captura pontual e modo de escuta contínua por hotword.
- **Sistema de migração de banco de dados** (`hermes.data.migrate`), com testes cobrindo migrações (`test_migrate.py`, `test_migration_v2.py`).
- **Empacotamento**: script de build para Windows via PyInstaller (`packaging/windows/build.bat`) e serviço systemd para Linux (`packaging/linux/install.sh` + `hermes.service`).
- **Suíte de testes**: 25 arquivos em `tests/`, usando `unittest`, cobrindo API, engine do assistente, banco, CLI, LLM, migrações, busca semântica, lembretes, etc.
- **Qualidade de código**: `ruff`, `black` e `isort` configurados via `pre-commit`.
- Documentação de apoio: tutorial para iniciantes, tutorial de uso avançado e explicação dos modos de voz (`docs/`).

## ⚠️ O que falta / pontos em aberto

Não havia um roadmap explícito no código no momento da pausa (não há `TODO`/`FIXME` relevantes nem issues documentadas), então esta lista é baseada na análise do estado atual — vale revisar e completar quando for retomar:

- **CHANGELOG desatualizado**: só existe a entrada `0.1.0` (ago/2025), apesar de ~105 PRs mesclados depois disso. Vale reconstruir o histórico ou pelo menos resumir os marcos principais.
- **Sem CI configurado**: não há workflows do GitHub Actions no repositório (`.github/workflows` não existe). Testes e lint rodam só localmente via `pre-commit`.
- **Sem Docker/containerização**: instalação depende de Python local + dependências do sistema (Vosk, PyQt5); não há imagem containerizada.
- **Busca semântica simples**: o índice padrão é TF-IDF; a interface `VectorIndex` já existe para plugar FAISS/Chroma, mas isso não foi implementado.
- **Instalação de voz manual**: o modelo Vosk pt-BR precisa ser baixado e descompactado manualmente (`~/.cache/vosk/...`) — poderia ser automatizado.
- **Cliente Caduceu com token em texto plano** no `config.yaml` de exemplo — revisar segurança antes de expor a API fora da rede local.
- **Sem release/instalador publicado**: os scripts de build existem (Windows/Linux), mas não há binário ou pacote distribuído.
- Vale revisar se GUI, CLI e API têm paridade de funcionalidades (não foi verificado a fundo nesta análise).

## 🏗️ Decisões técnicas

- **Linguagem**: Python 3.10+ (CI/dev usa 3.11).
- **Arquitetura em camadas**, dentro de `src/hermes/` (layout `src`):
  - `ui/` — CLI (`cli.py`) e GUI PyQt5 (`gui.py`).
  - `core/` — lógica principal do app e registro de ideias (`app.py`, `registro_ideias.py`, `prompts.py`).
  - `assistant/` — motor do assistente, estado e voz (`engine.py`, `state.py`, `voice.py`).
  - `services/` — integrações: banco (`db.py`), LLM (`llm_interface.py`), lembretes (`reminders.py`), busca semântica (`semantic_search.py`), voz/STT (`stt.py`).
  - `data/` — acesso a banco e migrações (`database.py`, `migrate.py`).
  - `api.py` — camada HTTP (FastAPI).
- **LLM local via Ollama**: comunicação HTTP com `http://localhost:11434/api/generate`; modelo, porta e timeout configuráveis por variável de ambiente ou argumento CLI (`HERMES_OLLAMA_MODEL`, `HERMES_API_PORT`, `HERMES_TIMEOUT`).
- **Banco de dados**: SQLite local (`hermes.db` por padrão, configurável via `HERMES_DB_PATH`), com sistema próprio de migrações versionadas.
- **Voz**: Vosk para reconhecimento offline (modelo pt-BR pequeno), pyttsx3 para síntese offline, `sounddevice` para captura de áudio.
- **Empacotamento de dependências via *extras*** no `pyproject.toml` (`voice`, `api`, `semantic`), permitindo instalação mínima (só GUI) ou completa.
- **Qualidade**: `ruff` + `black` + `isort` via `pre-commit`; testes com `unittest` (sem pytest).
- **Licença**: MIT.

## 📝 Notas para quando eu for retomar

1. Roda