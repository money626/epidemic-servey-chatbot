
class Error(Exception):
    pass


class CommandNotFoundError(Error):
    def __init__(self, expression: str, message: str) -> None:
        self.message = message
        self.expression = expression


class CommandNotImplementedError(Error):
    def __init__(self, expression: str, message: str) -> None:
        self.message = message
        self.expression = expression


class NoSuchUserError(Error):
    def __init__(self, message: str) -> None:
        self.message = message


class UserNotBindedError(Error):
    def __init__(self, message: str) -> None:
        self.message = message
