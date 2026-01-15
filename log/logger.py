import logging

def setup_logger(handler=None):
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