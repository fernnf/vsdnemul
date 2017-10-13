

class CommandError(Exception):
    """Base class for exceptions in this module."""
    pass


class LinkCommandError(CommandError):
    def __init__(self, type = "LinkCommandError:", message = None):
        super(LinkCommandError, self).__init__(type+" "+message)

