from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox, QListWidget, QLabel
)

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker
from settings.config import AppConfig

import json

class BoxiamentoCarga(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password
        self.pp_config = AppConfig()

        self.setup_ui()

    def setup_ui(self):
        # Data
        self.dt_entrega = QLineEdit(maxLength=8)
        self.dt_entrega.setPlaceholderText("DDMMAAAA")

        # Botão
        self.btn_executar = QPushButton("Executar Boxiamento de Cargas")
        self.btn_executar.clicked.connect(self.executar_boxiamento)

        self.label_rotas = QLabel("Selecione as rotas para boxiamento:")
        self.lista_rotas = QListWidget()
        self.lista_rotas.setSelectionMode(QListWidget.MultiSelection)
        self.carregar_rotas()

        # Layout
        form = QFormLayout()
        form.addRow("Data Entrega:", self.dt_entrega)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.label_rotas)
        layout.addWidget(self.lista_rotas)
        layout.addWidget(self.btn_executar)

        self.setLayout(layout)

    def executar_boxiamento(self):

        if not self.dt_entrega.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de entrega deve ser preenchida.")
            return
        
        rotas_selecionadas = [item.text().strip() for item in self.lista_rotas.selectedItems()]
        if not rotas_selecionadas:
            QMessageBox.warning(self, "Campo obrigatório", "Selecione pelo menos uma rota para boxiamento.")
            return
        
        self.btn_executar.setEnabled(False)

        params = {
            "action": "boxiamento",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "data": self.dt_entrega.text(),
            "rotas": rotas_selecionadas
        }

        self.thread = QThread()
        self.worker = PrwebWorker(params)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        
        self.thread.start()

    def on_finished(self):
        QMessageBox.information(self, "Concluído", "Boxiamento de carga concluído com sucesso.")
        self.btn_executar.setEnabled(True)

    def on_error(self, message):
        QMessageBox.critical(self, "Erro", message)
        self.btn_executar.setEnabled(True)

    def carregar_rotas(self):
        self.lista_rotas.clear()

        try:
            with open(self.app_config.ROTAS_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.app_config._ensure_rotas_file()
            with open(self.app_config.ROTAS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Erro no JSON", "O arquivo rotas.json está inválido.")
            return

        for rota in data.get("sp_rotas", []):
            self.lista_rotas.addItem(str(rota).strip())

        for i in range(self.lista_rotas.count()):
            self.lista_rotas.item(i).setSelected(True)