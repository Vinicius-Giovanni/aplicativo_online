from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QMessageBox
)

from log.qt_handler import QtLogHandler
from log.logger import setup_logger
from app.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPA - Boxiamento Online")
        self.setFixedSize(300, 200)

        self.filter_window = None
        self.setup_ui()

    def setup_ui(self):
        self.input_empresa = QLineEdit(maxLength=2)
        self.input_matricula = QLineEdit(maxLength=8)
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Logar")
        self.btn_login.clicked.connect(self.logar)

        form_layout = QFormLayout()
        form_layout.addRow("Empresa:", self.input_empresa)
        form_layout.addRow("Matrícula:", self.input_matricula)
        form_layout.addRow("Senha:", self.input_password)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def logar(self):
        empresa = self.input_empresa.text()
        matricula = self.input_matricula.text()
        password = self.input_password.text()

        if not empresa or not matricula or not password:
            QMessageBox.warning(self, "Campos obrigatórios", "empresa, matrícula e senha devem ser preenchidos.")
            return

        log_handler = QtLogHandler()
        logger = setup_logger(log_handler)

        logger.info("Aplicação iniciada")
        logger.info("Usuário autenticado com sucesso")

        self.main_window = MainWindow(
            empresa=empresa,
            matricula=matricula,
            password=password,
            log_handler=log_handler
        )

        self.main_window.logout_requested.connect(self.on_logout)

        self.main_window.show()
        self.hide()
    
    def on_logout(self):
        self.input_empresa.clear()
        self.input_matricula.clear()
        self.input_password.clear()
        self.show()