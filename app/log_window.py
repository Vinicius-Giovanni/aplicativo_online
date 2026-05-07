from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class LogWindow(QWidget):
    """
    Janela responsável pela exibição dos logs de execução da RPA.

    A classe cria uma interface simples contendo uma área de texto
    somente leitura utilizada para acompanhar mensagens e eventos
    gerados durante a execução do processo automatizado.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Acompanhamento da RPA")
        self.showMaximized()

        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_log)
        self.setLayout(layout)
    
    def append_log(self, message:str):
        """
        Adiciona uma nova mensagem na área de exibição de logs.

        Parâmetros:
            message (str):
                Mensagem que será exibida na interface.

        Retorno:
            None
        """

        self.text_log.append(message)
    