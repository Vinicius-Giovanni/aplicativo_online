from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QMessageBox
)

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker

class BoxiamentoCarga(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password

        self.setup_ui()

    def setup_ui(self):
        # Data
        self.dt_entrega = QLineEdit(maxLength=8)
        self.dt_entrega.setPlaceholderText("DDMMAAAA")

        # Botão
        self.btn_executar = QPushButton("Executar Boxiamento de Cargas")
        self.btn_executar.clicked.connect(self.executar_boxiamento)

        # Layout
        form = QFormLayout()
        form.addRow("Data Entrega:", self.dt_entrega)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_executar)

        self.setLayout(layout)

    def executar_boxiamento(self):

        if not self.dt_entrega.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de entrega deve ser preenchida.")
            return
        
        self.btn_executar.setEnabled(False)

        params = {
            "action": "boxiamento",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "data": self.dt_entrega.text()
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
