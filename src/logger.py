import logging
import logging.handlers
import sys
from pathlib import Path
from queue import Queue


def setup_logging() -> logging.handlers.QueueListener:
    lq: Queue = Queue(maxsize=10000)
    queue_handler = logging.handlers.QueueHandler(lq)
    queue_handler.setLevel(logging.DEBUG)

    std_formatter = logging.Formatter(
        "[%(levelname)s|%(asctime)s|%(module)s|L%(lineno)d] %(message)s"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(std_formatter)

    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/bot.log", maxBytes=10000000, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(std_formatter)

    listener = logging.handlers.QueueListener(
        lq, stdout_handler, file_handler, respect_handler_level=False
    )
    listener.start()

    logging.root.addHandler(queue_handler)
    logging.root.setLevel(logging.DEBUG)

    return listener


def get_logger() -> logging.Logger:
    return logging.getLogger("bot_logger")
