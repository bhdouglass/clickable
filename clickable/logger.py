import logging
import os


class Colors:
    DEBUG = '\033[94m'
    INFO = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CRITICAL = '\033[91m'
    CLEAR = '\033[0m'


class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = Colors.CLEAR
        if record.levelname == 'DEBUG':
            color = Colors.DEBUG
        elif record.levelname == 'INFO':
            color = Colors.INFO
        elif record.levelname == 'WARNING':
            color = Colors.WARNING
        elif record.levelname == 'ERROR':
            color = Colors.ERROR
        elif record.levelname == 'CRITICAL':
            color = Colors.CRITICAL

        record.msg = color + record.msg + Colors.CLEAR
        return super().format(record)


# TODO log to a file

logger = logging.getLogger('clickable')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(ColorFormatter())
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

try:
    log_dir = os.path.expanduser('~/.clickable')
    log_file = os.path.join(log_dir, 'clickable.log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if os.path.exists(log_file):
        os.unlink(log_file)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning('Failed to setup logging to ~/.clickable/clickable.log', exc_info=e)

