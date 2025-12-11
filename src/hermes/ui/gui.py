import csv
import json
import logging
import sys

import pyttsx3
import sounddevice as sd
import vosk
from PyQt5.QtCore import QFutureWatcher, QTimer, QtConcurrent, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..assistant import HotwordListener, engine
from ..assistant.state import ConversationState
from ..config import load_from_args
from ..core import app
from ..logging import setup_logging
from ..services.stt import get_vosk_model

LLM_FRIENDLY_MESSAGE = (
    "Não consegui falar com o modelo de linguagem. Verifique se o servidor está"
    " rodando em localhost:11434 e tente novamente."
)


logger = logging.getLogger(__name__)


class HotwordListenerThread(QThread):
    """Thread que encapsula o ``HotwordListener`` e expõe sinais Qt."""

    hotword_detected = pyqtSignal(str)
    command_detected = pyqtSignal(str)
    hotword_error = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._listener: HotwordListener | None = None
        self._stop_requested = False

    def run(self) -> None:  # pragma: no cover - integrações com áudio/threads
        try:
            class _QtHotwordListener(HotwordListener):
                def __init__(self, outer: HotwordListenerThread) -> None:
                    super().__init__()
                    self._outer = outer

                def on_hotword_detected(self, texto: str) -> None:
                    self._outer.hotword_detected.emit(texto)

                def on_command(self, texto: str) -> None:
                    self._outer.command_detected.emit(texto)

                def on_error(self, exc: Exception) -> None:
                    self._outer.hotword_error.emit(str(exc))

            self._listener = _QtHotwordListener(self)
            self._listener.start()
            while not self._stop_requested:
                self.msleep(100)
        except Exception as exc:
            logger.exception("Erro ao executar HotwordListenerThread")
            self.hotword_error.emit(str(exc))
        finally:
            if self._listener:
                try:
                    self._listener.stop()
                except Exception:  # pragma: no cover - melhor esforço
                    logger.exception("Falha ao encerrar HotwordListener")
            self._listener = None

    def stop(self) -> None:  # pragma: no cover - integrações com áudio/threads
        self._stop_requested = True


class HermesGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hermes - Registro de Ideias")
        self.setMinimumSize(500, 600)

        self.conversation_states: dict[int, ConversationState] = {}

        # Widgets
        self.user_label = QLabel("Usuário:")
        self.user_combo = QComboBox()
        self.new_user_button = QPushButton("Novo Usuário")
        self.new_user_button.clicked.connect(self.adicionar_usuario)

        self.title_label = QLabel("Título:")
        self.title_input = QLineEdit()
        self.title_mic = QPushButton("🎙️")
        self.title_mic.clicked.connect(lambda: self.capturar_fala("titulo"))
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_input)
        title_layout.addWidget(self.title_mic)

        self.desc_label = QLabel("Descrição:")
        self.desc_input = QTextEdit()
        self.desc_mic = QPushButton("🎙️")
        self.desc_mic.clicked.connect(lambda: self.capturar_fala("descricao"))
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(self.desc_input)
        desc_layout.addWidget(self.desc_mic)

        self.save_button = QPushButton("Salvar Ideia")
        self.save_button.clicked.connect(self.salvar_ideia)

        self.export_button = QPushButton("Exportar")
        self.export_button.clicked.connect(self.exportar_ideias)

        self.process_button = QPushButton("Processar com IA")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.processar_ideia_selecionada)

        # Busca e filtros
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_user_combo = QComboBox()
        self.search_user_combo.addItem("Todos", None)
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText("Data início (AAAA-MM-DD)")
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText("Data fim (AAAA-MM-DD)")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.buscar_ideias)
        self.search_watcher = QFutureWatcher()
        self.search_watcher.finished.connect(self._exibir_resultados_busca)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_user_combo)
        search_layout.addWidget(self.start_date_input)
        search_layout.addWidget(self.end_date_input)
        search_layout.addWidget(self.search_button)

        self.idea_list_label = QLabel("Ideias registradas:")
        self.idea_list = QListWidget()
        self.idea_list.itemDoubleClicked.connect(self.exibir_ideia_completa)
        self.idea_list.itemSelectionChanged.connect(self._atualizar_botao_processar)

        # Aba Assistente
        self.assistant_history = QTextEdit()
        self.assistant_history.setReadOnly(True)
        self.assistant_input = QLineEdit()
        self.assistant_input.returnPressed.connect(self.enviar_mensagem_assistente)
        self.assistant_send = QPushButton("Enviar")
        self.assistant_send.clicked.connect(self.enviar_mensagem_assistente)
        self.assistant_mic = QPushButton("🎙️")
        self.assistant_mic.clicked.connect(self.capturar_fala_assistente)
        self.assistant_tts_checkbox = QCheckBox("Falar resposta")
        self.continuous_listen_checkbox = QCheckBox("🎙️ Escuta contínua (Hermes)")
        self.continuous_listen_checkbox.setToolTip(
            "O áudio do modo de escuta contínua é processado localmente pelo Hermes.\n"
            "Nada é enviado para a internet.\n"
            "Para desligar, basta desmarcar esta opção."
        )
        self.continuous_listen_checkbox.toggled.connect(self._alternar_escuta_continua)
        self.hotword_sound_checkbox = QCheckBox("🔔 Aviso sonoro na hotword")
        self.hotword_sound_checkbox.setChecked(True)
        self.listener_status = QLabel("Hotword: inativa")
        self.hotword_indicator = QLabel("")
        self.hotword_indicator.setStyleSheet("color: #2e7d32; font-weight: bold;")
        self.listener_thread: HotwordListenerThread | None = None
        self._hotword_feedback_timer = QTimer(self)
        self._hotword_feedback_timer.setSingleShot(True)
        self._hotword_feedback_timer.timeout.connect(self._restore_listen_visuals)

        assistant_input_layout = QHBoxLayout()
        assistant_input_layout.addWidget(self.assistant_input)
        assistant_input_layout.addWidget(self.assistant_send)
        assistant_input_layout.addWidget(self.assistant_mic)

        listener_controls_layout = QHBoxLayout()
        listener_controls_layout.addWidget(self.continuous_listen_checkbox)
        listener_controls_layout.addWidget(self.hotword_sound_checkbox)

        listener_status_layout = QHBoxLayout()
        listener_status_layout.addWidget(self.listener_status)
        listener_status_layout.addWidget(self.hotword_indicator)
        listener_status_layout.addStretch()

        assistant_layout = QVBoxLayout()
        assistant_layout.addWidget(self.assistant_history)
        assistant_layout.addWidget(self.assistant_tts_checkbox)
        assistant_layout.addLayout(listener_controls_layout)
        assistant_layout.addLayout(listener_status_layout)
        assistant_layout.addLayout(assistant_input_layout)
        self.assistant_tab = QWidget()
        self.assistant_tab.setLayout(assistant_layout)

        # Layout principal com abas
        ideias_layout = QVBoxLayout()
        ideias_layout.addWidget(self.title_label)
        ideias_layout.addLayout(title_layout)
        ideias_layout.addWidget(self.desc_label)
        ideias_layout.addLayout(desc_layout)
        ideias_layout.addWidget(self.save_button)
        ideias_layout.addWidget(self.export_button)
        ideias_layout.addWidget(self.process_button)
        ideias_layout.addLayout(search_layout)
        ideias_layout.addWidget(self.idea_list_label)
        ideias_layout.addWidget(self.idea_list)
        ideias_tab = QWidget()
        ideias_tab.setLayout(ideias_layout)

        tab_widget = QTabWidget()
        tab_widget.addTab(ideias_tab, "Ideias")
        tab_widget.addTab(self.assistant_tab, "Assistente")

        layout = QVBoxLayout()
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_combo)
        layout.addWidget(self.new_user_button)
        layout.addWidget(tab_widget)

        self.setLayout(layout)

        self.carregar_usuarios()
        self.user_combo.currentIndexChanged.connect(self.listar_ideias)
        self.user_combo.currentIndexChanged.connect(self._atualizar_assistente_para_usuario)

        try:
            self.vosk_model = get_vosk_model()
        except Exception:
            logger.exception("Falha ao carregar modelo Vosk para captura de fala")
            raise

    def carregar_usuarios(self):
        self.user_combo.clear()
        self.search_user_combo.clear()
        self.search_user_combo.addItem("Todos", None)
        usuarios = app.listar_usuarios()
        for usuario in usuarios:
            display = f"{usuario['name']} ({usuario['kind']})"
            self.user_combo.addItem(display, usuario["id"])
            self.search_user_combo.addItem(display, usuario["id"])
        if usuarios:
            self.user_combo.blockSignals(True)
            self.user_combo.setCurrentIndex(0)
            self.user_combo.blockSignals(False)
            self.listar_ideias()
            self._atualizar_assistente_para_usuario()
        else:
            self.idea_list.clear()

    def salvar_ideia(self):
        usuario_id = self.user_combo.currentData()
        titulo = self.title_input.text().strip()
        descricao = self.desc_input.toPlainText().strip()

        if not usuario_id or not titulo or not descricao:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        ideia_salva = False
        try:
            resultado = app.registrar_ideia(usuario_id, titulo, descricao, usar_llm=True)
            llm_resposta = resultado.get("llm_response", "")
            mensagem_sucesso = "Ideia salva com sucesso."
            if llm_resposta:
                mensagem_sucesso += f"\n\nSugestões do modelo:\n{llm_resposta}"
            QMessageBox.information(self, "Sucesso", mensagem_sucesso)
            ideia_salva = True
        except RuntimeError as e:
            mensagem = str(e) or LLM_FRIENDLY_MESSAGE
            opcao = QMessageBox.question(
                self,
                "Erro",
                f"{mensagem}\n\nDeseja salvar a ideia mesmo assim?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if opcao == QMessageBox.Yes:
                app.registrar_ideia(usuario_id, titulo, descricao, usar_llm=False)
                QMessageBox.information(self, "Sucesso", "Ideia salva sem sugestões.")
                ideia_salva = True
            else:
                return
        if ideia_salva:
            engine = pyttsx3.init()
            engine.say("ideia salva")
            engine.runAndWait()
        self.title_input.clear()
        self.desc_input.clear()
        self.listar_ideias()

    def capturar_fala(self, campo: str) -> None:
        """Captura fala do microfone e preenche o campo indicado."""
        try:
            duracao = 5  # segundos
            sd.default.samplerate = 16000
            sd.default.channels = 1
            audio = sd.rec(int(duracao * sd.default.samplerate), dtype="int16")
            sd.wait()
            rec = vosk.KaldiRecognizer(self.vosk_model, sd.default.samplerate)
            rec.AcceptWaveform(audio.tobytes())
            texto = json.loads(rec.Result()).get("text", "")
            if campo == "titulo":
                self.title_input.setText(texto)
            else:
                self.desc_input.setPlainText(texto)
        except Exception as e:  # pragma: no cover - envolve hardware
            QMessageBox.warning(self, "Erro", f"Falha ao capturar fala: {e}")

    def capturar_fala_assistente(self) -> None:
        """Captura a fala do usuário e preenche a entrada do chat."""
        try:
            duracao = 5  # segundos
            sd.default.samplerate = 16000
            sd.default.channels = 1
            audio = sd.rec(int(duracao * sd.default.samplerate), dtype="int16")
            sd.wait()
            rec = vosk.KaldiRecognizer(self.vosk_model, sd.default.samplerate)
            rec.AcceptWaveform(audio.tobytes())
            texto = json.loads(rec.Result()).get("text", "")
            self.assistant_input.setText(texto)
        except Exception as e:  # pragma: no cover - envolve hardware
            QMessageBox.warning(self, "Erro", f"Falha ao capturar fala: {e}")

    def buscar_ideias(self):
        user_id = self.search_user_combo.currentData()
        texto = self.search_input.text().strip() or None
        self.search_button.setEnabled(False)
        future = QtConcurrent.run(app.buscar_ideias, user_id, texto=texto)
        self.search_watcher.setFuture(future)

    def _exibir_resultados_busca(self):
        ideias = self.search_watcher.future().result()
        inicio = self.start_date_input.text().strip()
        fim = self.end_date_input.text().strip()
        if inicio:
            ideias = [i for i in ideias if i["created_at"][:10] >= inicio]
        if fim:
            ideias = [i for i in ideias if i["created_at"][:10] <= fim]
        self.idea_list.clear()
        for ideia in ideias:
            item = QListWidgetItem(f"{ideia['created_at'][:10]} - {ideia['title']}")
            item.setData(1000, ideia)
            self.idea_list.addItem(item)
        self.search_button.setEnabled(True)
        self._atualizar_botao_processar()

    def listar_ideias(self):
        usuario_id = self.user_combo.currentData()
        self.idea_list.clear()
        if not usuario_id:
            return
        ideias = app.listar_ideias(usuario_id)
        for ideia in ideias:
            item = QListWidgetItem(f"{ideia['created_at'][:10]} - {ideia['title']}")
            item.setData(1000, ideia)  # Armazena a ideia completa
            self.idea_list.addItem(item)
        self._atualizar_botao_processar()

    def exportar_ideias(self):
        selecionados = self.idea_list.selectedItems()
        if not selecionados:
            QMessageBox.warning(self, "Erro", "Selecione ao menos uma ideia.")
            return
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Ideias",
            "",
            "CSV Files (*.csv);;Text Files (*.txt)",
        )
        if not caminho:
            return
        ideias = [item.data(1000) for item in selecionados]
        if caminho.lower().endswith(".txt"):
            with open(caminho, "w", encoding="utf-8") as f:
                for ideia in ideias:
                    f.write(
                        f"{ideia['created_at']} - {ideia['title']}\n{ideia['body']}\n\n"
                    )
        else:
            if not caminho.lower().endswith(".csv"):
                caminho += ".csv"
            with open(caminho, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["data", "titulo", "corpo"])
                writer.writerows(
                    (i["created_at"], i["title"], i["body"]) for i in ideias
                )
        QMessageBox.information(self, "Sucesso", "Ideias exportadas.")

    def exibir_ideia_completa(self, item):
        ideia = item.data(1000)
        QMessageBox.information(
            self,
            "Ideia Completa",
            f"📅 {ideia['created_at']}\n\n{ideia['title']}\n\n{ideia['body']}",
        )

    def _atualizar_botao_processar(self):
        self.process_button.setEnabled(bool(self.idea_list.selectedItems()))

    def processar_ideia_selecionada(self):
        selecionados = self.idea_list.selectedItems()
        if not selecionados:
            return
        item = selecionados[0]
        ideia = item.data(1000)
        try:
            sugestoes = app.processar_ideia(
                ideia["id"], ideia["title"], ideia["body"]
            )
            ideia["llm_summary"] = sugestoes.get("llm_summary")
            ideia["llm_topic"] = sugestoes.get("llm_topic")
            ideia["tags"] = sugestoes.get("tags")
            item.setData(1000, ideia)
        except RuntimeError as e:  # pragma: no cover - interface gráfica
            QMessageBox.warning(self, "Erro", str(e) or LLM_FRIENDLY_MESSAGE)
        except Exception as e:  # pragma: no cover - interface gráfica
            QMessageBox.warning(self, "Erro", str(e))

    def adicionar_usuario(self):
        nome, ok = QInputDialog.getText(self, "Novo Usuário", "Nome do usuário:")
        if not ok or not nome.strip():
            return
        tipo, ok = QInputDialog.getText(self, "Novo Usuário", "Tipo do usuário:")
        if not ok or not tipo.strip():
            return
        user_id = app.criar_usuario(nome.strip(), tipo.strip())
        self.carregar_usuarios()
        idx = self.user_combo.findData(user_id)
        if idx != -1:
            self.user_combo.setCurrentIndex(idx)

    def _obter_state_atual(self) -> ConversationState | None:
        user_id = self.user_combo.currentData()
        if user_id is None:
            return None
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = ConversationState(user_id=user_id)
        return self.conversation_states[user_id]

    def _atualizar_assistente_para_usuario(self) -> None:
        state = self._obter_state_atual()
        self.assistant_history.clear()
        if not state or not state.history:
            return
        for entrada in state.history:
            role = entrada.get("role", "user")
            prefixo = "Você" if role == "user" else "Hermes"
            conteudo = entrada.get("content", "")
            self.assistant_history.append(f"{prefixo}: {conteudo}")

    def enviar_mensagem_assistente(self) -> None:
        mensagem = self.assistant_input.text()
        self._processar_mensagem_assistente(mensagem)

    def _processar_mensagem_assistente(self, mensagem: str, origem_voz: bool = False) -> None:
        mensagem_limpa = mensagem.strip()
        state = self._obter_state_atual()
        if not mensagem_limpa:
            return
        if state is None:
            QMessageBox.warning(
                self,
                "Erro",
                "Selecione um usuário antes de conversar com o Hermes.",
            )
            return

        prefixo = "Você (voz)" if origem_voz else "Você"
        self.assistant_history.append(f"{prefixo}: {mensagem_limpa}")
        if not origem_voz:
            self.assistant_input.clear()

        resposta = engine.responder_mensagem(mensagem_limpa, state=state)
        self.assistant_history.append(f"Hermes: {resposta}")

        if self.assistant_tts_checkbox.isChecked() and resposta:
            engine_tts = pyttsx3.init()
            engine_tts.say(resposta)
            engine_tts.runAndWait()

    def _atualizar_estado_mic_continuo(self, ativo: bool) -> None:
        tooltip = "Desativado enquanto a escuta contínua está ativa."
        for botao_mic in (self.title_mic, self.desc_mic, self.assistant_mic):
            botao_mic.setEnabled(not ativo)
            botao_mic.setToolTip(tooltip if ativo else "")

    def _alternar_escuta_continua(self, habilitar: bool) -> None:
        if habilitar:
            if self.listener_thread and self.listener_thread.isRunning():
                return
            self.listener_thread = HotwordListenerThread(self)
            self.listener_thread.hotword_detected.connect(self._on_hotword_detected)
            self.listener_thread.command_detected.connect(self._on_command_detected)
            self.listener_thread.hotword_error.connect(self._on_hotword_error)
            logger.info("Ativando escuta contínua do Hermes")
            self.listener_thread.start()
            self.assistant_history.append("[Hermes] Escuta contínua ativada.")
            self._restore_listen_visuals()
            self._atualizar_estado_mic_continuo(True)
        else:
            if self.listener_thread:
                self.listener_thread.stop()
                self.listener_thread.wait()
                self.listener_thread = None
            logger.info("Desativando escuta contínua do Hermes")
            self.listener_status.setText("Hotword: inativa")
            self.assistant_history.append("[Hermes] Escuta contínua desativada.")
            self.listener_status.setStyleSheet("")
            self.assistant_tab.setStyleSheet("")
            self.hotword_indicator.clear()
            self._hotword_feedback_timer.stop()
            self._atualizar_estado_mic_continuo(False)

    def _on_hotword_detected(self, texto: str) -> None:
        self.listener_status.setText("🟢 Hotword: detectada!")
        self.assistant_history.append(f"[Hermes] Hotword detectada: {texto}")
        self.listener_status.setStyleSheet("color: green;")
        if self.hotword_sound_checkbox.isChecked():
            QApplication.beep()
        self._hotword_feedback_timer.stop()
        self.assistant_tab.setStyleSheet(
            "border: 2px solid #4caf50; background-color: #e6ffe6;"
        )
        self.hotword_indicator.setText("👂 Ouvindo...")
        self._hotword_feedback_timer.start(1500)

    def _on_command_detected(self, texto: str) -> None:
        self._restore_listen_visuals()
        self.assistant_history.append(f"[Hermes] Comando capturado: {texto}")
        self._processar_mensagem_assistente(texto, origem_voz=True)

    def _on_hotword_error(self, mensagem: str) -> None:
        logger.error("Erro na escuta contínua: %s", mensagem)
        QMessageBox.warning(
            self,
            "Microfone indisponível",
            "Não foi possível iniciar a escuta contínua.\n"
            "Verifique o microfone e tente novamente.\n"
            f"Detalhes: {mensagem}",
        )
        self.continuous_listen_checkbox.blockSignals(True)
        self.continuous_listen_checkbox.setChecked(False)
        self.continuous_listen_checkbox.blockSignals(False)
        if self.listener_thread:
            self.listener_thread.wait()
            self.listener_thread = None
        self.listener_status.setText("Hotword: inativa")
        self.listener_status.setStyleSheet("color: red;")
        self.assistant_tab.setStyleSheet("")
        self.hotword_indicator.clear()
        self._hotword_feedback_timer.stop()
        self._atualizar_estado_mic_continuo(False)

    def _restore_listen_visuals(self) -> None:
        if self.listener_thread:
            self.listener_status.setText("🟢 Hotword: aguardando...")
            self.listener_status.setStyleSheet("color: green;")
            self.assistant_tab.setStyleSheet("border: 2px solid #4caf50;")
        else:
            self.listener_status.setStyleSheet("")
            self.assistant_tab.setStyleSheet("")
        self.hotword_indicator.clear()


def main(argv: list[str] | None = None) -> None:
    """Inicia a interface gráfica do Hermes."""

    setup_logging()
    load_from_args(argv)
    app.inicializar()

    qt_app = QApplication(sys.argv)
    gui = HermesGUI()
    gui.show()
    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main()
