import uuid
import logging
import pygogo as gogo


class Logger(object):

    def __init__(self, level = "info"):
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_ = gogo.Gogo("gercom.vsdnagent",
                         low_formatter = formatter,
                         low_hdlr = gogo.handlers.file_hdlr('vsdn_agent.log'),
                         high_level = level,
                         high_formatter = formatter)

    @classmethod
    def logger(cls, name = "", level = "info"):
        log = cls(level = level)
        return log.log_.get_logger(name = name)