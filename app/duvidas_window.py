from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QToolButton,
    QFrame,
)
class TopicoExpansivel(QFrame):
    def __init__(self, titulo: str, conteudo: str):
        super().__init__()
        self.setObjectName("DuvidaTopico")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.botao = QToolButton()
        self.botao.setObjectName("DuvidasTopicoBotao")
        self.botao.setText(titulo)
        self.botao.setCheckable(True)
        self.botao.setChecked(False)
        self.botao.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.botao.clicked.connect(self._alternar)

        self.texto = QLabel(conteudo)
        self.texto.setObjectName("DuvidaTopicoTexto")
        self.texto.setWordWrap(True)
        self.texto.setVisible(False)
        self.texto.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(self.botao)
        layout.addWidget(self.texto)

    def _alternar(self):
        expandido = self.botao.isChecked()
        simbolo = "▼" if expandido else "▶"
        titulo_base = self.botao.text().split(" ", 1)[1] if " " in self.botao.text() else self.botao.text()
        self.botao.setText(f"{simbolo} {titulo_base}")
        self.texto.setVisible(expandido)
    
class DuvidasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("DuvidasWindow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("About Us • Dúvidas")
        titulo.setObjectName("Title")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        subtitulo = QLabel("Clique em cada tópico para expandir o conteúdo.")
        subtitulo.setObjectName("DuvidasSubtitle")

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        topicos = [
            (
                "▶ Como usar a ferramenta",
                "A aplicação foi criada para automatizar o fluxo no PRWEB com foco em produtividade, "
                "redução de erro manual e padronização operacional.",
            ),
            (
                "▶ Filtrar Cargas",
                "Acesse 📤 Emitir Cargas para emitir automaticamente rotas específicas. "
                "A emissão considera os dados de acesso informados no login e os filtros aplicados. "
                "Sempre valide o registro (log) para confirmar sucesso da operação.",
            ),
            (
                "▶ Emitir Cargas",
                "Acesse 📤 Emitir Cargas para emitir automaticamente rotas específicas. "
                "A emissão considera os dados de acesso informados no login e os filtros aplicados. "
                "Sempre valide o registro (log) para confirmar sucesso da operação.",
            ),
            (
                "▶ Boxiamento de Carga",
                "Em📦 Boxiamento de Carga, o sistema direciona as cargas para o box correto. "
                "O boxiamento pode seguir regras por transportadora e também por rota específica, "
                "conforme configuração cadastrada.",
            ),
            (
                "▶ Configurar novas transportadoras e condições de boxiamento",
                "Abra ⚙️ Configurações para manter as regras do sistema. "
                "Em Rotas SP, adicione ou remova rotas priorizadas para operação. "
                "Em Cargas / Box, você pode cadastrar: "
                "- Regra por transportadora: carga + box. "
                "– Regra por rota: deixe a carga em branco e informe rota + box. "
                "Clique em Salvar para gravar as alterações. "
                "Use Restaurar padrões para voltar à configuração original, quando necessário. ",
            ),
            (
                "▶ Registro e Exportação",
                "Use o Registro para acompanhar a execução em tempo real e exporte. "
                "logs para auditoria e histórico.",
            ),
            (
                "▶ Boas práticas",
                "Revise rotas e regras antes de rodar em produção, teste com pequenos "
                "volumes e consulte histórico e Registro em caso de divergência.",
            ),
        ]

        for titulo_topico, conteudo in topicos:
            layout.addWidget(TopicoExpansivel(titulo_topico, conteudo))

        layout.addStretch()

