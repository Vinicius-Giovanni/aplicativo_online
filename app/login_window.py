from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout ,QFormLayout, QMessageBox, QLabel, QFrame
)

from log.qt_handler import QtLogHandler
from log.logger import setup_logger
from app.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle("RPA - Boxiamento Online")
        self.setFixedSize(1024, 640)

        self.background_path = Path(__file__).resolve().parent / 'assets' / 'images' / 'fundo_teste.png'
        self.filter_window = None
        self.setup_ui()

    def setup_ui(self):
        background_label = QLabel(self)
        background_label.setObjectName("BackgroundImage")
        background_label.setGeometry(0, 0, self.width(), self.height())
        bg_pixmap = QPixmap(str(self.background_path))
        if not bg_pixmap.isNull():
            background_label.setPixmap(bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        background_label.lower()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 18, 32, 18)
        root_layout.setSpacing(12)

        top_bar = QHBoxLayout(self)
        brand = QLabel("♜ Online")
        brand.setObjectName("BrandLabel")

        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(18)
        for text in ['Login', 'About Us', 'Register', 'Contact']:
            item = QLabel(text)
            item.setObjectName("TopMenu")
            if text == "Login":
                item.setProperty("active", True)
            menu_layout.addWidget(item)

        top_bar.addWidget(brand)
        top_bar.addStretch()
        top_bar.addLayout(menu_layout)
        root_layout.addLayout(top_bar)

        form_area = QVBoxLayout()
        form_area.setSpacing(16)

        self.input_empresa = QLineEdit(maxLength=2)
        self.input_empresa.setPlaceholderText("29 or 21")

        self.input_matricula = QLineEdit(maxLength=8)
        self.input_matricula.setPlaceholderText("Matrícula")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Entrar")
        self.btn_login.setObjectName("PrimaryButton")
        self.btn_login.clicked.connect(self.logar)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setHorizontalSpacing(10)
        form_layout.setVerticalSpacing(14)

        user_icon = QLabel("👤")
        pass_icon = QLabel("🔒")

        user_row = QHBoxLayout()
        user_row.setSpacing(10)
        user_row.addWidget(user_icon)
        user_row.addWidget(self.input_matricula)

        pass_row = QHBoxLayout()
        pass_row.setSpacing(10)
        pass_row.addWidget(pass_icon)
        pass_row.addWidget(self.input_password)

        user_widget = QFrame()
        user_widget.setObjectName("InputRow")
        user_widget.setLayout(user_row)

        pass_widget = QFrame()
        pass_widget.setObjectName("InputRow")
        pass_widget.setLayout(pass_row)

        form_layout.addRow("", self.input_empresa)
        form_layout.addRow("", user_widget)
        form_layout.addRow("", pass_widget)

        card = QFrame()
        card.setObjectName("LoginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.addLayout(form_layout)
        card_layout.addWidget(self.btn_login)

        form_area.addStretch()
        form_area.addWidget(card, alignment=Qt.AlignHCenter)
        form_area.addStretch()
        root_layout.addLayout(form_area)

        footer = QHBoxLayout()
        footer.addWidget(QLabel("About Us"))
        footer.addWidget(QLabel("Privacy Policy"))
        footer.addWidget(QLabel("Terms Of Use"))
        footer.addStretch()
        footer.addWidget(QLabel("© 2021 Key. All Rights Reserved | Design By Vinicíus Giovanni"))

        for i in range(footer.count()):
            item = footer.itemAt(i).widget()
            if isinstance(item, QLabel):
                item.setObjectName("FooterLabel")

        root_layout.addLayout(footer)

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