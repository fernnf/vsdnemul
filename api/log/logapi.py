import logging
import logging.config

logging.config.fileConfig('logging.conf')


def get_logger(name):
    return logging.getLogger(name = name)