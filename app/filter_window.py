from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout,
    QFormLayout, QCheckBox, QComboBox, QMessageBox
)

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker

class FilterWindow(QWidget):
    def __init__(self, empresa, matricula, password):
        super().__init__()
        
        self.empresa = empresa
        self.matricula = matricula
        self.password = password

        self.setup_ui()

    def setup_ui(self):
        # Datas
        self.dt_exp_retro = QLineEdit(maxLength=8)
        self.dt_exp_retro.setPlaceholderText("DDMMAAAA")
        self.dt_exp_post = QLineEdit(maxLength=8)
        self.dt_exp_post.setPlaceholderText("DDMMAAAA")
        self.dt_exp_start = QLineEdit(maxLength=8)
        self.dt_exp_start.setPlaceholderText("DDMMAAAA")
        self.dt_exp_end = QLineEdit(maxLength=8)
        self.dt_exp_end.setPlaceholderText("DDMMAAAA")
        self.dt_entrega = QLineEdit(maxLength=8)
        self.dt_entrega.setPlaceholderText("DDMMAAAA")

        # Checkboxes (Sim / Não)
        self.cb_mono = QCheckBox("Pedidos Mono")
        self.cb_multiplo = QCheckBox("Pedidos Múltiplos")
        self.cb_b2b = QCheckBox("Programação B2B")
        self.cb_b2c = QCheckBox("Programação B2C")
        self.cb_cross = QCheckBox("Programação Crossdocking")

        # Modalidade
        self.modalidade = QComboBox()
        self.modalidade.addItems([
            "OUTRAS TRANSPORTADORAS (LEVE)",
            "ENTREGA PELOS CORREIOS"
        ])

        # Botão
        self.btn_executar = QPushButton("Executar Filtragem")
        self.btn_executar.clicked.connect(self.executar_filtragem)

        # Layout
        form = QFormLayout()
        form.addRow("Data Limite Expedição Retroativa:", self.dt_exp_retro)
        form.addRow("Data Limite Expedição Posterior:", self.dt_exp_post)
        form.addRow("Data Limite Expedição Início:", self.dt_exp_start)
        form.addRow("Data Limite Expedição Fim:", self.dt_exp_end)
        form.addRow("Data Entrega:", self.dt_entrega)
        form.addRow("Modalidade:", self.modalidade)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.cb_mono)
        layout.addWidget(self.cb_multiplo)
        layout.addWidget(self.cb_b2b)
        layout.addWidget(self.cb_b2c)
        layout.addWidget(self.cb_cross)
        layout.addWidget(self.btn_executar)

        self.setLayout(layout)

    # Conversao checkbox sim/nao
    def yes_no(self, checkbox):
        return "Sim" if checkbox.isChecked() else "Não"

    def executar_filtragem(self):

        if not self.dt_entrega.text():
            QMessageBox.warning(self, "Campo obrigatório", "A data de entrega deve ser preenchida.")
            return

        self.btn_executar.setEnabled(False)

        params = {
            "action": "filtragem",
            "empresa": self.empresa,
            "matricula": self.matricula,
            "password": self.password,
            "dt_limite_exp_retro": self.dt_exp_retro.text(),
            "dt_limite_exp_posterior": self.dt_exp_post.text(),
            "dt_limite_exp_start": self.dt_exp_start.text(),
            "dt_limite_exp_end": self.dt_exp_end.text(),
            "dt_entrega": self.dt_entrega.text(),
            "mono": self.yes_no(self.cb_mono),
            "multiplo": self.yes_no(self.cb_multiplo),
            "B2B": self.yes_no(self.cb_b2b),
            "B2C": self.yes_no(self.cb_b2c),
            "CROSSDOCKING": self.yes_no(self.cb_cross),
            "modalidade": self.modalidade.currentText()
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
        QMessageBox.information(self, "Concluído", "Filtragem de cargas concluída.")
        self.btn_executar.setEnabled(True)
    
    def on_error(self, message):
        QMessageBox.critical(self, "Erro", message)
        self.btn_executar.setEnabled(True)








