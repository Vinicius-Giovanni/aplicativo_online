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

from app.filter_window import FilterWindow
from app.emissao_window import EmissaoWindow
from app.boxiamento_de_carga import BoxiamentoCarga
from app.log_window import LogWindow
from app.config_window import ConfigWindow
from app.log_export_window import LogExportWindow

class MainWindow(QMainWindow):

    logout_requested = Signal()

    def __init__(self,empresa,matricula,password,log_handler):
        super().__init__()

        self.empresa = empresa
        self.matricula = matricula
        self.password = password

        self.setWindowTitle("RPA - Online")

        self.setup_topbar()

        self.showMaximized()

        self.windows = {}

        self.setup_sidebar()
        self.setup_central()
        self.setup_log_dock(log_handler)

    # setup de login
    def setup_topbar(self):
        """
        Configura a barra superior da aplicação.

        A função cria a toolbar principal contendo informações
        do usuário autenticado e versão atual da aplicação.

        Retorno:
            None
        """

        """
        MAJOR.MINOR.PATCH
        1.0.0

        MAJOR => Mudança que quebra compatibilidade
        MIJOR => Nova feature
        PATCH => Correção de bug
        """

        vs = str("4.8.13")

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
        """
        Configura o menu lateral da aplicação.

        A função cria os botões de navegação responsáveis
        por acessar as funcionalidades disponíveis no sistema.

        Lógica utilizada:
            - Cria os botões do menu lateral.
            - Conecta cada botão ao método correspondente.
            - Organiza os componentes no layout lateral.

        Retorno:
            None
        """
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("PRWEB")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)

        # filter button
        btn_filtrar = QPushButton("🔍 Filtrar Cargas")
        btn_filtrar.clicked.connect(self.abrir_filtragem)

        # emitter button
        btn_emitir = QPushButton("📤 Emitir Cargas")
        btn_emitir.clicked.connect(self.abrir_emissao)

        # boxiamento
        btn_boxiamento = QPushButton("📦 Boxiamento de Carga")
        btn_boxiamento.clicked.connect(self.abrir_boxiamento)

        # configurações
        btn_configuracoes = QPushButton("⚙️ Configurações")
        btn_configuracoes.clicked.connect(self.abrir_configuracoes)

        # export log
        btn_export_logs = QPushButton("🗂️ Histórico")
        btn_export_logs.clicked.connect(self.abrir_exportacao_logs)

        # logout
        btn_logout = QPushButton("Sair")
        btn_logout.clicked.connect(self.logout)

        # log
        btn_logs = QPushButton("📝 Registro")
        btn_logs.clicked.connect(self.toggle_logs)

        # posicao botoes
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(btn_filtrar)
        layout.addWidget(btn_emitir)
        layout.addWidget(btn_boxiamento)
        layout.addWidget(btn_configuracoes)
        layout.addWidget(btn_export_logs)
        layout.addStretch()
        layout.addWidget(btn_logs)
        layout.addWidget(btn_logout)
        

        sidebar.setLayout(layout)

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self._wrap_as_dock(sidebar)
        )

    def _wrap_as_dock(self, widget):
        """
        Encapsula um widget em um componente dockável.

        A função cria um QDockWidget configurado para uso
        como painel lateral fixo da aplicação.

        Parâmetros:
            widget:
                Componente que será encapsulado.

        Retorno:
            QDockWidget:
                Dock configurado.
        """
        dock = QDockWidget()
        dock.setTitleBarWidget(QWidget()) # remove title
        dock.setWidget(widget)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        return dock
    
    # centro
    def setup_central(self):
        """
        Configura a área central da aplicação.

        A função inicializa o sistema de páginas utilizando
        um QStackedWidget e registra todas as telas disponíveis
        para navegação.

        Lógica utilizada:
            - Cria a tela inicial.
            - Inicializa as páginas da aplicação.
            - Adiciona as páginas na pilha de navegação.
            - Define o widget central da janela.

        Retorno:
            None
        """
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

        self.config_page = ConfigWindow()
        self.log_export_page = LogExportWindow()

        self.stack.addWidget(home)
        self.stack.addWidget(self.filter_page)
        self.stack.addWidget(self.emissao_page)
        self.stack.addWidget(self.boxiamento_page)
        self.stack.addWidget(self.config_page)
        self.stack.addWidget(self.log_export_page)
        self.setCentralWidget(self.stack)
    
    # dock
    def setup_log_dock(self,log_handler):
        """
        Configura o painel dockável de logs da aplicação.

        A função conecta os sinais do sistema de logs às interfaces
        de exibição e cria o painel responsável pelo monitoramento
        dos registros em tempo real.

        Parâmetros:
            log_handler:
                Manipulador responsável pelos eventos de log.

        Retorno:
            None
        """
        self.log_window = LogWindow()

        log_handler.emitter.log_sinal.connect(
            self.log_window.append_log
        )
        log_handler.emitter.log_sinal.connect(
            self.log_export_page.append_log
        )

        self.log_dock = QDockWidget("Registros")
        self.log_dock.setWidget(self.log_window)
        self.log_dock.setAllowedAreas(
            Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea 
        )

        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        self.log_dock.hide()

    def toggle_logs(self):
        """
        Alterna a visibilidade do painel de logs.

        Retorno:
            None
        """
        self.log_dock.setVisible(not self.log_dock.isVisible())

    # open windows
    def abrir_filtragem(self):
        """
        Abre a página de filtragem de cargas.

        A função altera a página atual da aplicação
        e garante a exibição do painel de logs.

        Retorno:
            None
        """
        self.stack.setCurrentIndex(1)
        if self.log_dock:
            self.log_dock.show()
    
    def abrir_emissao(self):
        """
        Abre a página de emissão de cargas.

        A função realiza o carregamento das rotas necessárias,
        altera a página atual e exibe o painel de logs.

        Retorno:
            None
        """
        self.emissao_page.carregar_rotas()
        self.stack.setCurrentIndex(2)
        if self.log_dock:
            self.log_dock.show()

    def abrir_boxiamento(self):
        """
        Abre a página de boxiamento de cargas.

        A função realiza o carregamento das rotas necessárias,
        altera a página atual e exibe o painel de logs.

        Retorno:
            None
        """
        self.boxiamento_page.carregar_rotas()
        self.stack.setCurrentIndex(3)
        if self.log_dock:
            self.log_dock.show()
    
    def abrir_configuracoes(self):
        """
        Abre a página de configurações da aplicação.

        A função carrega as configurações atuais do sistema,
        altera a página exibida e mostra o painel de logs.

        Retorno:
            None
        """
        self.config_page.carregar_configuracoes()
        self.stack.setCurrentIndex(4)
        if self.log_dock:
            self.log_dock.show()

    def abrir_exportacao_logs(self):
        """
        Abre a página de exportação e histórico de logs.

        Retorno:
            None
        """
        self.stack.setCurrentIndex(5)
        if self.log_dock:
            self.log_dock.show()

    def abrir_duvidas(self):
        """
        Abre a página de dúvidas ou informações da aplicação.

        Retorno:
            None
        """
        self.stack.setCurrentIndex(6)
        if self.log_dock:
            self.log_dock.show()

    def logout(self):
        """
        Realiza o logout da aplicação.

        A função emite o sinal de logout e encerra
        a janela principal da aplicação.

        Retorno:
            None
        """
        self.logout_requested.emit()
        self.close()