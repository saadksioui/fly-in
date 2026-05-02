class ParsingException(Exception):
    pass


class HubException(ParsingException):
    pass


class ConnectionException(ParsingException):
    pass
