from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

class DuvidasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Dúvidas")
        titulo.setObjectName("Title")
        titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        texto = QLabel(
            """
<b>Como usar a ferramenta</b><br><br>
A aplicação foi criada para automatizar o fluxo no PRWEB com foco em produtividade,
redução de erro manual e padronização operacional.<br><br>

<b>1) Filtrar Cargas</b><br>
• Use a tela <b>🔍 Filtrar Cargas</b> para buscar e organizar cargas disponíveis.<br>
• Essa etapa ajuda a validar rapidamente o que será processado em emissão e boxiamento.<br><br>

<b>2) Emitir Cargas</b><br>
• Acesse <b>📤 Emitir Cargas</b> para emitir automaticamente rotas específicas.<br>
• A emissão considera os dados de acesso informados no login e os filtros aplicados.<br>
• Sempre valide o registro (log) para confirmar sucesso da operação.<br><br>

<b>3) Boxiamento de Carga</b><br>
• Em <b>📦 Boxiamento de Carga</b>, o sistema direciona as cargas para o box correto.
• O boxiamento pode seguir regras por transportadora e também por rota específica,
conforme configuração cadastrada.<br><br>

<b>4) Configurar novas transportadoras e condições de boxiamento</b><br>
• Abra <b>⚙️ Configurações</b> para manter as regras do sistema.<br>
• Em <b>Rotas SP</b>, adicione ou remova rotas priorizadas para operação.<br>
• Em <b>Cargas / Box</b>, você pode cadastrar:<br>
&nbsp;&nbsp;– Regra por transportadora: <i>carga + box</i>.<br>
&nbsp;&nbsp;– Regra por rota: deixe a carga em branco e informe <i>rota + box</i>.<br>
• Clique em <b>Salvar</b> para gravar as alterações.
• Use <b>Restaurar padrões</b> para voltar à configuração original, quando necessário.<br><br>

<b>5) Registro e Exportação</b><br>
• Use <b>📝 Registro</b> para acompanhar em tempo real tudo que a automação executa.<br>
• Em <b>💾 Exportar Registro</b>, salve os logs para auditoria, suporte e histórico.<br><br>

<b>Boas práticas</b><br>
• Revise rotas e regras antes de rodar em produção.<br>
• Faça testes com pequenos volumes ao alterar configurações.
• Consulte os logs sempre que houver divergências de emissão ou boxiamento.
"""
        )
        texto.setWordWrap(True)
        texto.setTextFormat(Qt.RichText)
        texto.setTextInteractionFlags(Qt.TextSelectableByMouse)
        texto.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        conteudo = QWidget()
        conteudo_layout = QVBoxLayout()
        conteudo_layout.addWidget(texto)
        conteudo_layout.addStretch()
        conteudo.setLayout(conteudo_layout)

        scroll.setWidget(conteudo)

        layout.addWidget(titulo)
        layout.addWidget(scroll)
        self.setLayout(layout)