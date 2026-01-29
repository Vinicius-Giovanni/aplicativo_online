from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QFrame,
    QDockWidget
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QToolBar

from PySide6.QtCore import QThread
from workers.prweb_worker import PrwebWorker

from app.filter_window import FilterWindow
from app.emissao_window import EmissaoWindow
from app.boxiamento_de_carga import BoxiamentoCarga
from app.log_window import LogWindow

class MainWindow(QMainWindow):

    logout_requested = Signal()

    def __init__(self,empresa,matricula,password,log_handler):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password

        self.setWindowTitle("RPA - Online")

        self.setup_topbar()
        self.setup_log_dock(log_handler)

        self.showMaximized()

        self.windows = {}

        self.setup_sidebar()
        self.setup_central()

    # setup de login
    def setup_topbar(self):

        vs = str("1.7.2")

        topbar = QToolBar()
        topbar.setMovable(False)

        label_user = QLabel(
            f"Empresa: {self.empresa} | Matrícula: {self.matricula} | Versão: {vs}"
        )

        label_user.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label_user.setObjectName("UserInfo")

        topbar.addWidget(label_user)

        self.addToolBar(Qt.TopToolBarArea, topbar)
        
    # sidebar
    def setup_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("PRWEB")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        # filter button
        btn_filtrar = QPushButton("Filtrar Cargas")
        btn_filtrar.clicked.connect(self.abrir_filtragem)

        # emitter button
        btn_emitir = QPushButton("Emitir Cargas")
        btn_emitir.clicked.connect(self.abrir_emissao)

        # boxiamento
        btn_boxiamento = QPushButton("Boxiamento de Carga")
        btn_boxiamento.clicked.connect(self.abrir_boxiamento)


        # logout
        btn_logout = QPushButton("Sair")
        btn_logout.clicked.connect(self.logout)

        # log
        btn_logs = QPushButton("Registro")
        btn_logs.clicked.connect(self.toggle_logs)

        # posicao botoes
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(btn_filtrar)
        layout.addWidget(btn_emitir)
        layout.addWidget(btn_boxiamento)
        layout.addStretch()
        layout.addWidget(btn_logs)
        layout.addWidget(btn_logout)
        

        sidebar.setLayout(layout)

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self._wrap_as_dock(sidebar)
        )

    def _wrap_as_dock(self, widget):
        dock = QDockWidget()
        dock.setTitleBarWidget(QWidget()) # remove title
        dock.setWidget(widget)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        return dock
    
    # centro
    def setup_central(self):
        self.stack = QStackedWidget()

        # tela inicial
        home = QWidget()
        home_layout = QVBoxLayout()
        welcome = QLabel("Selecione uma ação no menu lateral")
        welcome.setAlignment(Qt.AlignCenter)

        home_layout.addStretch()
        home_layout.addWidget(welcome)
        home_layout.addStretch()
        home.setLayout(home_layout)

        # windows
        self.filter_page = FilterWindow(
            empresa=self.empresa,
            matricula=self.matricula,
            password=self.password
        )

        self.emissao_page = EmissaoWindow(
            empresa=self.empresa,
            matricula=self.matricula,
            password=self.password
        )

        self.boxiamento_page = BoxiamentoCarga(
            empresa=self.empresa,
            matricula=self.matricula,
            password=self.password
        )

        self.stack.addWidget(home)
        self.stack.addWidget(self.filter_page)
        self.stack.addWidget(self.emissao_page)
        self.stack.addWidget(self.boxiamento_page)
        self.setCentralWidget(self.stack)
    
    # dock
    def setup_log_dock(self,log_handler):
        self.log_window = LogWindow()

        log_handler.emitter.log_sinal.connect(
            self.log_window.append_log
        )

        self.log_dock = QDockWidget("Registros")
        self.log_dock.setWidget(self.log_window)
        self.log_dock.setAllowedAreas(
            Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea 
        )

        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        self.log_dock.hide()

    def toggle_logs(self):
        self.log_dock.setVisible(not self.log_dock.isVisible())

    # open windows
    def abrir_filtragem(self):
        self.stack.setCurrentIndex(1)
        if self.log_dock:
            self.log_dock.show()
    
    def abrir_emissao(self):
        self.stack.setCurrentIndex(2)
        if self.log_dock:
            self.log_dock.show()

    def abrir_boxiamento(self):
        self.stack.setCurrentIndex(3)
        if self.log_dock:
            self.log_dock.show()


    def logout(self):
        self.logout_requested.emit()
        self.close()