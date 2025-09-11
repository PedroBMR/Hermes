import csv
import json
import sys

import pyttsx3
import sounddevice as sd
import vosk

from PyQt5.QtCore import QFutureWatcher, QtConcurrent
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.registro_ideias import analisar_ideia_com_llm, registrar_ideia_com_llm
from ..data.database import buscar_usuarios, criar_usuario
from ..services.db import add_idea, list_ideas, search_ideas, update_idea
from ..services.reminders import start_scheduler


class HermesGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hermes - Registro de Ideias")
        self.setMinimumSize(500, 600)

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

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_combo)
        layout.addWidget(self.new_user_button)
        layout.addWidget(self.title_label)
        layout.addLayout(title_layout)
        layout.addWidget(self.desc_label)
        layout.addLayout(desc_layout)
        layout.addWidget(self.save_button)
        layout.addWidget(self.export_button)
        layout.addWidget(self.process_button)
        layout.addLayout(search_layout)
        layout.addWidget(self.idea_list_label)
        layout.addWidget(self.idea_list)

        self.setLayout(layout)

        self.carregar_usuarios()
        self.user_combo.currentIndexChanged.connect(self.listar_ideias)

        # Modelo de reconhecimento de fala Vosk
        self.vosk_model = vosk.Model(lang="pt-br")

    def carregar_usuarios(self):
        self.user_combo.clear()
        self.search_user_combo.clear()
        self.search_user_combo.addItem("Todos", None)
        usuarios = buscar_usuarios()
        self.usuarios_map = {}
        for uid, nome, tipo in usuarios:
            display = f"{nome} ({tipo})"
            self.user_combo.addItem(display)
            self.search_user_combo.addItem(display, uid)
            self.usuarios_map[display] = uid
        if usuarios:
            self.user_combo.blockSignals(True)
            self.user_combo.setCurrentIndex(0)
            self.user_combo.blockSignals(False)
            self.listar_ideias()
        else:
            self.idea_list.clear()

    def salvar_ideia(self):
        usuario_display = self.user_combo.currentText()
        titulo = self.title_input.text().strip()
        descricao = self.desc_input.toPlainText().strip()

        if not usuario_display or not titulo or not descricao:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        usuario_id = self.usuarios_map.get(usuario_display)
        ideia_salva = False
        try:
            sugestoes = registrar_ideia_com_llm(usuario_id, titulo, descricao)
            QMessageBox.information(
                self,
                "Sucesso",
                f"Ideia salva com sucesso.\n\nSugestões do modelo:\n{sugestoes}",
            )
            ideia_salva = True
        except RuntimeError as e:
            opcao = QMessageBox.question(
                self,
                "Erro",
                f"{e}\n\nDeseja salvar a ideia mesmo assim?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if opcao == QMessageBox.Yes:
                add_idea(usuario_id, titulo, descricao)
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

    def buscar_ideias(self):
        user_id = self.search_user_combo.currentData()
        texto = self.search_input.text().strip() or None
        self.search_button.setEnabled(False)
        future = QtConcurrent.run(search_ideas, user_id, texto)
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
        usuario_display = self.user_combo.currentText()
        usuario_id = self.usuarios_map.get(usuario_display)
        self.idea_list.clear()
        if not usuario_id:
            return
        ideias = list_ideas(usuario_id)
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
            sugestoes = analisar_ideia_com_llm(ideia["title"], ideia["body"])
            update_idea(
                ideia["id"],
                llm_summary=sugestoes["llm_summary"],
                llm_topic=sugestoes["llm_topic"],
            )
            ideia["llm_summary"] = sugestoes["llm_summary"]
            ideia["llm_topic"] = sugestoes["llm_topic"]
            item.setData(1000, ideia)
        except Exception as e:  # pragma: no cover - interface gráfica
            QMessageBox.warning(self, "Erro", str(e))

    def adicionar_usuario(self):
        nome, ok = QInputDialog.getText(self, "Novo Usuário", "Nome do usuário:")
        if not ok or not nome.strip():
            return
        tipo, ok = QInputDialog.getText(self, "Novo Usuário", "Tipo do usuário:")
        if not ok or not tipo.strip():
            return
        criar_usuario(nome.strip(), tipo.strip())
        self.carregar_usuarios()
        display = f"{nome.strip()} ({tipo.strip()})"
        idx = self.user_combo.findText(display)
        if idx != -1:
            self.user_combo.setCurrentIndex(idx)


def main() -> None:
    """Inicia a interface gráfica do Hermes."""
    start_scheduler()
    app = QApplication(sys.argv)
    gui = HermesGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
