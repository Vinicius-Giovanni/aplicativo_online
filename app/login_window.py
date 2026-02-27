from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QMessageBox, QLabel, QFrame
)

from PySide6.QtCore import Qt
from log.qt_handler import QtLogHandler
from log.logger import setup_logger
from app.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle("RPA - Boxiamento Online")
        self.setFixedSize(420, 320)

        self.filter_window = None
        self.setup_ui()

    def setup_ui(self):
        self.input_empresa = QLineEdit(maxLength=2)
        self.input_empresa.setPlaceholderText("Ex.: 29 ou 21")

        self.input_matricula = QLineEdit(maxLength=8)
        self.input_matricula.setPlaceholderText("Sua matrícula")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Sua senha")
        self.input_password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Entrar")
        self.btn_login.setObjectName("PrimayButton")
        self.btn_login.clicked.connect(self.logar)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.addRow("Empresa", self.input_empresa)
        form_layout.addRow("Matrícula", self.input_matricula)
        form_layout.addRow("Senha", self.input_password)

        card = QFrame()
        card.setObjectName("LoginCard")

        card_layout = QVBoxLayout()
        card_layout.setSpacing(14)

        title = QLabel("Bem-vindo")
        title.setObjectName("LoginTitle")

        subtitle = QLabel("Acesse o RPA Online para continuar")
        subtitle.setObjectName("LoginSubtitle")

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addLayout(form_layout)
        card_layout.addWidget(self.btn_login)
        card.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 24, 30, 24)
        layout.addStretch()
        layout.addWidget(card)
        layout.addStretch()
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