import logging


def setup_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


logger_main = setup_logger('main')
logger_openai = setup_logger("open-ai")
logger_cosmos = setup_logger("cosmos-db")
logger_mysql = setup_logger("mysql-db")