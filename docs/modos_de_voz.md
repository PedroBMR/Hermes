# Modos de voz do Hermes

O Hermes oferece duas formas de entrada por voz: captura pontual (botões de microfone) e escuta contínua com hotword. Ambos funcionam 100% offline usando o modelo Vosk instalado localmente.

## Pré-requisitos

- Microfone configurado no sistema operacional.
- Pacote `vosk` instalado e modelo de voz extraído em `~/.cache/vosk/...`.
- Para síntese de voz (TTS) opcional nas respostas: `pyttsx3`.

---

## 1. Modo de voz pontual (botão de mic)

**Como funciona:**

- Disponível na GUI nos campos de **Título**, **Descrição** e na entrada do chat do assistente.
- Cada clique no botão `🎙️` grava ~5 segundos de áudio, transcreve localmente e preenche o campo escolhido.
- A captura ocorre apenas durante essa janela curta; depois o microfone é liberado.

**Quando usar:**

- Para ditar rapidamente o texto de um campo específico.
- Quando não é necessário manter o microfone ativo o tempo todo.

**Passo a passo (GUI):**

1. Garanta que o Vosk esteja instalado e o modelo de voz esteja disponível.
2. Clique no botão `🎙️` ao lado do campo desejado.
3. Fale normalmente até o tempo expirar; o texto aparecerá no campo.
4. Edite ou salve a ideia normalmente.

---

## 2. Modo de escuta contínua (hotword “Hermes”)

**Como funciona:**

- Mantém o microfone ativo ouvindo a hotword **“Hermes”**. Após detectar a hotword, o Hermes captura a frase seguinte como comando para o assistente.
- Funciona tanto na GUI quanto na CLI e processa áudio localmente.

**Como ativar/desativar:**

- **GUI:** marque a opção **"🎙️ Escuta contínua (Hermes)"** na aba do assistente. Use novamente o checkbox para desligar. A opção **"🔔 Aviso sonoro na hotword"** toca um beep quando a hotword é reconhecida.
- **CLI:** escolha a opção **7. Escuta contínua por voz** no menu principal. Pressione **Ctrl+C** para encerrar quando quiser.

**Como falar com ele:**

1. Diga “**Hermes**” próximo ao microfone.
2. Após a detecção, fale o comando ou pergunta (ex.: “Hermes, liste minhas ideias de viagem”).
3. A resposta aparece no chat do assistente; na CLI ela é exibida no terminal. Se o TTS estiver ativado, o Hermes também fala a resposta.

**Indicações visuais e feedback:**

- **GUI:**
  - Status “Hotword: aguardando…” quando ativo.
  - Ao detectar a hotword, o painel do assistente fica destacado em verde e o texto “👂 Ouvindo...” aparece; opcionalmente um beep é emitido.
  - O histórico exibe mensagens como `[Hermes] Hotword detectada` e `[Hermes] Comando capturado`.
- **CLI:** logs informam “Escutando... pressione Ctrl+C para encerrar” e “Hotword detectada: ...”, seguidos pelo comando reconhecido e a resposta do Hermes.

**Limitações e cuidados:**

- Consome o microfone de forma contínua enquanto o modo estiver ativo.
- Pode ser mais sensível a ruídos ou palavras parecidas com “Hermes”; use em ambientes silenciosos para melhor precisão.
- Todo o processamento é offline; não há envio de áudio para servidores externos.

---

## Qual modo escolher?

- Use **voz pontual** para preencher campos específicos ou quando preferir controlar manualmente quando o microfone é usado.
- Use **escuta contínua** para conversar de forma hands-free com o assistente, emitindo comandos após dizer a hotword.
