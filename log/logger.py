import logging

def setup_logger(handler=None):
    """
    Configura e retorna o logger principal da aplicação.

    A função inicializa o logger da RPA, define o nível
    de registro das mensagens e aplica o formatter utilizado
    na padronização dos logs.

    Lógica utilizada:
        - Obtém ou cria o logger principal da aplicação.
        - Define o nível de log como INFO.
        - Configura o padrão de formatação das mensagens.
        - Adiciona o handler informado ao logger.

    Parâmetros:
        handler:
            Manipulador responsável pelo destino dos logs.
            Pode ser utilizado para integração com interface gráfica,
            arquivos ou terminal.

    Retorno:
        logging.Logger:
            Instância configurada do logger principal.
    """
    logger = logging.getLogger("RPA")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    if handler:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger