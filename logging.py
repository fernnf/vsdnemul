import logging
import pygogo as gogo
import uuid


class Logger(object):
    @staticmethod
    def logger():
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        return gogo.Gogo("gercom.vsdnagent",
                         low_formatter = formatter,
                         low_hdlr = gogo.handlers.file_hdlr('{id}_vsdn_log.log'.format(id = uuid.uuid4())),
                         high_level = "info",
                         high_formatter = formatter)

