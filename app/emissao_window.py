from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox
)

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker

class EmissaoWindow(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password

        self.setup_ui()

    def setup_ui(self):
        # Data
        self.data = QLineEdit(maxLength=8)
        self.data.setPlaceholderText("DDMMAAAA")

        # Botão
        self.btn_executar = QPushButton("Executar Emissão")
        self.btn_executar.clicked.connect(self.executar_emissao)

        # Layout
        form = QFormLayout()
        form.addRow("Data Entrega:", self.data)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_executar)

        self.setLayout(layout)
    
    def executar_emissao(self):
        
        if not self.data.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de entrega deve ser preenchida.")
            return
        
        self.btn_executar.setEnabled(False)

        params = {
            "action": "emissao",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "data": self.data.text()
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
        QMessageBox.information(self, "Concluído", "Emissão de cargas concluída com sucesso.")
        self.btn_executar.setEnabled(True)

    def on_error(self, message):
        QMessageBox.critical(self, "Erro", message)
        self.btn_executar.setEnabled(True)