from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QFrame
)

from log.qt_handler import QtLogHandler
from log.logger import setup_logger
from app.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle("RPA - Boxiamento Online")
        self.setMinimumSize(1024, 640)

        self.background_path = Path(__file__).resolve().parent / 'assets' / 'images' / 'fundo_teste.png'
        self.background_label = None
        self.filter_window = None
        self.setup_ui()

    def setup_ui(self):
        self.background_label = QLabel(self)
        self.background_label.setObjectName("BackgroundImage")
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self._refresh_background()
        self.background_label.lower()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(12)

        top_bar_frame = QFrame(self)
        top_bar_frame.setFixedHeight(110)
        top_bar_frame.setStyleSheet("""
            background-color: rgba(9, 54, 102, 0.70);
            border: none;
        """)
        top_bar_frame.setObjectName("LoginTopBar")
        top_bar_layout = QHBoxLayout(top_bar_frame)
        top_bar_layout.setContentsMargins(20, 10, 20, 10)

        brand = QLabel("♜ Online")
        brand.setObjectName("BrandLabel")

        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(18)
        for text in ['About Us']:
            item = QLabel(text)
            item.setObjectName("TopMenu")
            if text == "Login":
                item.setProperty("active", True)
            menu_layout.addWidget(item)

        top_bar_layout.addWidget(brand)
        top_bar_layout.addStretch()
        top_bar_layout.addLayout(menu_layout)
        root_layout.addWidget(top_bar_frame)

        form_area = QVBoxLayout()
        form_area.setContentsMargins(32, 12, 32, 0)
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

        form_layout = QVBoxLayout()
        form_layout.setSpacing(14)

        empresa_widget = self._build_input_row(self.input_empresa, "🏢")
        user_widget = self._build_input_row(self.input_matricula, "👤")
        pass_widget = self._build_input_row(self.input_password, "🔒")

        form_layout.addWidget(empresa_widget)
        form_layout.addWidget(user_widget)
        form_layout.addWidget(pass_widget)

        card = QFrame()
        card.setObjectName("LoginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.addLayout(form_layout)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.btn_login)

        form_area.addStretch()
        form_area.addWidget(card, alignment=Qt.AlignHCenter)
        form_area.addStretch()
        root_layout.addLayout(form_area)

        footer = QHBoxLayout()
        footer.setContentsMargins(32, 0, 32, 18)
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

    def _build_input_row(self, line_edit: QLineEdit, icon_text: str) -> QFrame:
        icon = QLabel(icon_text)
        icon.setObjectName("InputIcon")

        row = QHBoxLayout()
        row.setContentsMargins(16, 4, 16, 4)
        row.setSpacing(10)
        row.addWidget(line_edit)
        row.addWidget(icon)

        wrapper = QFrame()
        wrapper.setObjectName("InputRow")
        wrapper.setLayout(row)
        return wrapper
    
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self.background_label is not None:
            self.background_label.setGeometry(0, 0, self.width(), self.height())
            self._refresh_background()

    def _refresh_background(self):
        bg_pixmap = QPixmap(str(self.background_path))
        if bg_pixmap.isNull() or self.background_label is None:
            return

        self.background_label.setPixmap(
            bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )

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
        self.showMaximized()