"""Utilitários de detecção de hotword usando Vosk."""

from __future__ import annotations

import json
import logging
import threading
import unicodedata
from typing import Optional

import sounddevice as sd
import vosk

logger = logging.getLogger(__name__)


def _normalizar_texto(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .lower()
    )


class HotwordListener:
    """Listener contínuo que detecta uma hotword no áudio do microfone."""

    STATE_IDLE = "idle"
    STATE_AWAITING_COMMAND = "awaiting_command"

    def __init__(
        self,
        hotword: str = "hermes",
        model_path: str | None = None,
        samplerate: int = 16000,
        block_duration: float = 0.5,
        device: Optional[int | str] = None,
    ) -> None:
        """Cria um listener que detecta a hotword configurada.

        Args:
            hotword: Palavra-chave a ser detectada no áudio.
            model_path: Caminho opcional para um modelo Vosk. Caso não seja
                informado, usa ``vosk.Model(lang="pt-br")``.
            samplerate: Taxa de amostragem do áudio capturado.
            block_duration: Duração (em segundos) de cada bloco de captura.
            device: Dispositivo de áudio a ser usado pelo ``sounddevice``.
        """

        self.hotword = _normalizar_texto(hotword or "")
        self._samplerate = samplerate
        self._blocksize = int(samplerate * block_duration)
        self._device = device
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._state = self.STATE_IDLE

        logger.info("Carregando modelo Vosk para hotword '%s'", self.hotword)
        self._model = vosk.Model(model_path) if model_path else vosk.Model(lang="pt-br")
        self._recognizer = vosk.KaldiRecognizer(self._model, samplerate)

    def start(self) -> None:
        """Inicia a captura de áudio e o loop de detecção da hotword."""

        if self._thread and self._thread.is_alive():
            logger.debug("HotwordListener já está em execução")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info("HotwordListener iniciado")

    def stop(self) -> None:
        """Encerra a captura de áudio sem travar o aplicativo."""

        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("HotwordListener finalizado")

    def on_hotword_detected(self, texto: str) -> None:  # pragma: no cover - callback
        """Callback chamado quando a hotword é detectada.

        Subclasses ou clientes podem sobrescrever este método para reagir à
        detecção. O texto reconhecido completo é repassado no parâmetro
        ``texto``.
        """

        logger.info("Hotword '%s' detectada: %s", self.hotword, texto)

    def _listen_loop(self) -> None:
        try:
            with sd.RawInputStream(
                samplerate=self._samplerate,
                blocksize=self._blocksize,
                device=self._device,
                dtype="int16",
                channels=1,
            ) as stream:
                while not self._stop_event.is_set():
                    data, _ = stream.read(self._blocksize)
                    if not data:
                        continue
                    if self._recognizer.AcceptWaveform(data):
                        resultado = json.loads(self._recognizer.Result())
                        self._process_result(resultado.get("text", ""), is_final=True)
                    else:
                        parcial = json.loads(self._recognizer.PartialResult())
                        self._process_result(parcial.get("partial", ""), is_final=False)
        except Exception:
            logger.exception("Erro no loop de escuta do HotwordListener")

    def _process_result(self, texto: str, *, is_final: bool) -> None:
        if not texto:
            return

        texto_normalizado = _normalizar_texto(texto)
        if self._state == self.STATE_IDLE:
            if self.hotword in texto_normalizado:
                logger.info("Hotword '%s' detectada no texto: %s", self.hotword, texto)
                self._state = self.STATE_AWAITING_COMMAND
                try:
                    self.on_hotword_detected(texto)
                except Exception:  # pragma: no cover - callback de usuário
                    logger.exception("Erro ao executar callback de hotword")
        elif self._state == self.STATE_AWAITING_COMMAND:
            if not is_final:
                return
            if texto_normalizado == self.hotword:
                logger.debug("Ignorando resultado final apenas com a hotword")
                return

            logger.info("Comando detectado: %s", texto)
            try:
                self.on_command(texto)
            except Exception:  # pragma: no cover - callback de usuário
                logger.exception("Erro ao executar callback de comando")
            finally:
                self._state = self.STATE_IDLE
                logger.debug("Retornando ao estado idle")

    def on_command(self, texto: str) -> None:  # pragma: no cover - callback
        """Callback chamado quando um comando é detectado após a hotword."""

        logger.info("Comando recebido: %s", texto)
