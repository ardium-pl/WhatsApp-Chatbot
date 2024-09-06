import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pytz

# Define the timezone for Poland
POLAND_TZ = pytz.timezone('Europe/Warsaw')


class PolandFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Convert the timestamp to the Poland timezone
        dt = datetime.fromtimestamp(record.created, POLAND_TZ)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


def setup_logger(name, log_file, level=logging.INFO):
    formatter = PolandFormatter('%(asctime)s %(levelname)s %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.encoding = 'utf-8'
    logger.addHandler(console_handler)

    return logger


# Ensure log directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Create loggers
main_logger = setup_logger('[Main]', os.path.join(log_dir, 'main.log'))
mysql_logger = setup_logger('[Mysql]', os.path.join(log_dir, 'mysql.log'))
cosmosdb_logger = setup_logger('[Cosmosdb]', os.path.join(log_dir, 'cosmosdb.log'))
openai_logger = setup_logger('[Openai]', os.path.join(log_dir, 'openai.log'))
whatsapp_logger = setup_logger('[Whatsapp]', os.path.join(log_dir, 'whatsapp.log'))
