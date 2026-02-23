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

        descricao = QLabel("Rotas SP")
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

        self.btn_remover = QPushButton("Excluir rota selecionada")
        self.btn_remover.clicked.connect(self.remover_rota)

        self.btn_recarregar = QPushButton("Recarregar")
        self.btn_reccaregar.clicked.connect(self.carregar_rotas)

        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_rotas)

        actions_layout.addWidget(self.btn_remover)
        actions_layout.addWidget(self.btn_recarregar)
        actions_layout.addWidget(self.btn_salvar)
        layout.addLayout(actions_layout)

        
