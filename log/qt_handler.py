import logging
from PySide6.QtCore import QObject, Signal

class QtLogEmitter(QObject):
    """
    Emissor de sinais para integração entre logging e interface Qt.

    A classe encapsula um sinal responsável por transmitir mensagens
    de log para componentes da interface gráfica de forma reativa.
    """

    log_sinal = Signal(str)

class QtLogHandler(logging.Handler):
    """
    Handler personalizado para integração do sistema de logging com Qt.

    A classe intercepta eventos de log do sistema padrão do Python
    e os encaminha para a interface gráfica por meio de sinais Qt.
    """
    def __init__(self):
        super().__init__()
        self.emitter = QtLogEmitter()

    def emit(self, record):
        """
        Processa e envia uma mensagem de log para a interface Qt.

        A função formata o registro de log recebido e emite o sinal
        para atualização em tempo real na interface gráfica.

        Parâmetros:
            record:
                Registro de log gerado pelo sistema de logging.

        Retorno:
            None
        """
        msg = self.format(record)
        self.emitter.log_sinal.emit(msg)

        