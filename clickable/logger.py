import logging


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
console = logging.StreamHandler()
console.setFormatter(ColorFormatter())

logger.setLevel(logging.INFO)
logger.addHandler(console)
