import json

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
)

from settings.config import AppConfig


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.app_config = AppConfig()
        self.setup_ui()
        self.carregar_rotas()

    def setup_ui(self):
        layout = QVBoxLayout()

        descricao = QLabel("Rotas SP (sp_rotas)")
        layout.addWidget(descricao)

        self.lista_rotas = QListWidget()
        self.lista_rotas.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.lista_rotas)

        add_layout = QHBoxLayout()
        self.input_rota = QLineEdit()
        self.input_rota.setPlaceholderText("Digite a nova rota")

        self.btn_add = QPushButton("Adicionar")
        self.btn_add.clicked.connect(self.adicionar_rota)

        add_layout.addWidget(self.input_rota)
        add_layout.addWidget(self.btn_add)
        layout.addLayout(add_layout)

        actions_layout = QHBoxLayout()

        self.btn_remover = QPushButton("Excluir selecionada")
        self.btn_remover.clicked.connect(self.remover_rota)

        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_recarregar.clicked.connect(self.carregar_rotas)

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_rotas)

        actions_layout.addWidget(self.btn_remover)
        actions_layout.addWidget(self.btn_recarregar)
        actions_layout.addWidget(self.btn_salvar)
        layout.addLayout(actions_layout)

        self.setLayout(layout)

    def carregar_rotas(self):
        self.lista_rotas.clear()

        try:
            with open(self.app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            QMessageBox.warning(self, "Arquivo não encontrado", "rotas.json não encontrado. Será recriado com padrão.")
            self.app_config._ensure_rotas_file()
            with open(self.app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erro no JSON", "O arquivo rotas.json está inválido.")
            return

        for rota in data.get("sp_rotas", []):
            self.lista_rotas.addItem(str(rota).strip())

    def adicionar_rota(self):
        rota = self.input_rota.text().strip()

        if not rota:
            QMessageBox.warning(self, "Campo vazio", "Digite uma rota para adicionar.")
            return

        rotas_existentes = [self.lista_rotas.item(i).text() for i in range(self.lista_rotas.count())]
        if rota in rotas_existentes:
            QMessageBox.information(self, "Rota duplicada", "Essa rota já está cadastrada.")
            return

        self.lista_rotas.addItem(rota)
        self.input_rota.clear()

    def remover_rota(self):
        item = self.lista_rotas.currentItem()

        if not item:
            QMessageBox.warning(self, "Seleção obrigatória", "Selecione uma rota para excluir.")
            return

        self.lista_rotas.takeItem(self.lista_rotas.row(item))

    def salvar_rotas(self):
        rotas = [self.lista_rotas.item(i).text().strip() for i in range(self.lista_rotas.count())]

        data = {"sp_rotas": rotas}

        try:
            with open(self.app_config.ROTAS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Não foi possível salvar rotas.json.\n{e}")
            return

        QMessageBox.information(self, "Sucesso", "Rotas salvas com sucesso.")