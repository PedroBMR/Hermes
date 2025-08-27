import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QInputDialog,
)
from .database import buscar_usuarios, salvar_ideia, listar_ideias as listar_ideias_db, criar_usuario

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

        self.desc_label = QLabel("Descrição:")
        self.desc_input = QTextEdit()

        self.save_button = QPushButton("Salvar Ideia")
        self.save_button.clicked.connect(self.salvar_ideia)

        self.idea_list_label = QLabel("Ideias registradas:")
        self.idea_list = QListWidget()
        self.idea_list.itemDoubleClicked.connect(self.exibir_ideia_completa)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_combo)
        layout.addWidget(self.new_user_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.desc_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.idea_list_label)
        layout.addWidget(self.idea_list)

        self.setLayout(layout)

        self.carregar_usuarios()
        self.user_combo.currentIndexChanged.connect(self.listar_ideias)

    def carregar_usuarios(self):
        self.user_combo.clear()
        usuarios = buscar_usuarios()
        self.usuarios_map = {}
        for uid, nome, tipo in usuarios:
            display = f"{nome} ({tipo})"
            self.user_combo.addItem(display)
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
        salvar_ideia(usuario_id, f"{titulo}\n\n{descricao}")
        QMessageBox.information(self, "Sucesso", "Ideia salva com sucesso.")
        self.title_input.clear()
        self.desc_input.clear()
        self.listar_ideias()
    def listar_ideias(self):
        usuario_display = self.user_combo.currentText()
        usuario_id = self.usuarios_map.get(usuario_display)
        self.idea_list.clear()
        if not usuario_id:
            return
        ideias = listar_ideias_db(usuario_id)
        for texto, data in ideias:
            item = QListWidgetItem(f"{data[:10]} - {texto.splitlines()[0]}")
            item.setData(1000, (data, texto))  # Armazena a ideia completa no item
            self.idea_list.addItem(item)

    def exibir_ideia_completa(self, item):
        data, texto = item.data(1000)
        QMessageBox.information(self, "Ideia Completa", f"📅 {data}\n\n{texto}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HermesGUI()
    gui.show()
    sys.exit(app.exec_())
