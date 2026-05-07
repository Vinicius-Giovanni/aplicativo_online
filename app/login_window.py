from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QLabel, QFrame, QSizePolicy
)

from log.qt_handler import QtLogHandler
from log.logger import setup_logger
from app.duvidas_window import DuvidasWindow
from app.main_window import MainWindow

class LoginWindow(QWidget):
    """
    Janela responsável pela autenticação do usuário na aplicação.

    A classe gerencia a interface de login, validação dos campos,
    inicialização do sistema de logs e abertura da janela principal
    após autenticação.
    """
        
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle("RPA - Boxiamento Online")

        self.background_path = Path(__file__).resolve().parent / 'assets' / 'images' / 'fundo_teste.png'
        self.background_label = None
        self.filter_window = None
        self.setup_ui()

    def setup_ui(self):
        """
        Configura os componentes visuais da interface de login.

        A função cria a estrutura principal da tela, incluindo
        imagem de fundo, barra superior, campos de autenticação,
        botão de login e rodapé da aplicação.

        Lógica utilizada:
            - Define os layouts principais da interface.
            - Configura os campos de entrada do usuário.
            - Cria os componentes visuais da tela.
            - Conecta os eventos dos botões às ações correspondentes.

        Parâmetros:
            self:
                Instância atual da classe.

        Retorno:
            None
        """ 

        self.background_label = QLabel(self)
        self.background_label.setObjectName("BackgroundImage")
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self._refresh_background()
        self.background_label.lower()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(12)

        top_bar_frame = QFrame(self)
        top_bar_frame.setObjectName("LoginTopBar")
        top_bar_layout = QHBoxLayout(top_bar_frame)
        top_bar_layout.setContentsMargins(20, 10, 20, 10)

        brand = QLabel("♜ RPA - Boxeamento de Cargas Online")
        brand.setObjectName("BrandLabel")

        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(18)

        self.btn_about = QPushButton('About Us')
        self.btn_about.setObjectName("TopMenu")
        self.btn_about.clicked.connect(self.abrir_duvidas)

        self.btn_about.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_about.setFixedHeight(32)

        menu_layout.addWidget(self.btn_about)

        top_bar_layout.addWidget(brand)
        top_bar_layout.addStretch()
        top_bar_layout.addLayout(menu_layout)
        root_layout.addWidget(top_bar_frame)

        form_area = QVBoxLayout()
        form_area.setContentsMargins(32, 12, 32, 0)
        form_area.setSpacing(16)

        self.input_empresa = QLineEdit(maxLength=2)
        self.input_empresa.setPlaceholderText("29 ou 21")

        self.input_matricula = QLineEdit(maxLength=8)
        self.input_matricula.setPlaceholderText("Matrícula")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("ENTRAR")
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
        footer.addStretch()
        footer.addWidget(QLabel("© 2026 Key. All Rights Reserved | Design By Vinicíus Giovanni"))

        for i in range(footer.count()):
            item = footer.itemAt(i).widget()
            if isinstance(item, QLabel):
                item.setObjectName("FooterLabel")

        root_layout.addLayout(footer)

    def _build_input_row(self, line_edit: QLineEdit, icon_text: str) -> QFrame:
        """
        Cria um componente visual contendo um campo de entrada e um ícone.

        A função encapsula a criação das linhas de entrada utilizadas
        no formulário de login.

        Parâmetros:
            line_edit (QLineEdit):
                Campo de entrada que será exibido.

            icon_text (str):
                Texto ou ícone associado ao campo.

        Retorno:
            QFrame:
                Componente visual configurado.
        """

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
        """
        Atualiza o tamanho da imagem de fundo durante o redimensionamento da janela.

        A função redefine a geometria do plano de fundo e reaplica
        o redimensionamento proporcional da imagem.

        Parâmetros:
            event (QResizeEvent):
                Evento de redimensionamento da janela.

        Retorno:
            None
        """

        super().resizeEvent(event)
        if self.background_label is not None:
            self.background_label.setGeometry(0, 0, self.width(), self.height())
            self._refresh_background()

    def _refresh_background(self):
        """
        Atualiza a imagem de fundo da interface.

        A função realiza o carregamento da imagem definida e aplica
        o redimensionamento proporcional ao tamanho atual da janela.

        Parâmetros:
            self:
                Instância atual da classe.

        Retorno:
            None
        """

        bg_pixmap = QPixmap(str(self.background_path))
        if bg_pixmap.isNull() or self.background_label is None:
            return

        self.background_label.setPixmap(
            bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )

    def logar(self):
        """
        Realiza o processo de autenticação e inicialização da aplicação.

        A função valida os campos de entrada, inicializa o sistema
        de logs, cria a janela principal da aplicação e realiza
        a transição da tela de login.

        Lógica utilizada:
            - Obtém os dados informados pelo usuário.
            - Valida o preenchimento obrigatório dos campos.
            - Inicializa o logger da aplicação.
            - Cria a janela principal do sistema.
            - Conecta o evento de logout.
            - Exibe a aplicação principal e oculta a tela de login.

        Parâmetros:
            self:
                Instância atual da classe.

        Retorno:
            None
        """

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

    def abrir_duvidas(self):
        """
        Abre a janela de informações e suporte da aplicação.

        A função cria a janela de dúvidas caso ela ainda não exista
        e garante sua exibição em primeiro plano.

        Parâmetros:
            self:
                Instância atual da classe.

        Retorno:
            None
        """
        if not hasattr(self, "duvidas_window") or self.duvidas_window is None:
            self.duvidas_window = DuvidasWindow()

        self.duvidas_window.setWindowTitle("About Us")
        self.duvidas_window.resize(800, 640)
        self.duvidas_window.show()
        self.duvidas_window.raise_()
        self.duvidas_window.activateWindow()
    
    def on_logout(self):
        """
        Realiza o processo de logout da aplicação.

        A função limpa os dados preenchidos no formulário de login
        e reexibe a janela principal de autenticação.

        Parâmetros:
            self:
                Instância atual da classe.

        Retorno:
            None
        """
        self.input_empresa.clear()
        self.input_matricula.clear()
        self.input_password.clear()
        self.showMaximized()