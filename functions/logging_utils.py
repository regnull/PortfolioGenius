import logging
from google.cloud import logging as cloud_logging
from google.cloud.logging_v2.handlers import StructuredLogHandler

_logger = None

def get_logger(name: str = "portfolio_genius") -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger
    client = cloud_logging.Client()
    handler = StructuredLogHandler()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    _logger = logger
    return logger
