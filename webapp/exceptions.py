from pprint import pformat


class WebAppError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, pformat(self.message))


class NoSuchEntityError(WebAppError):
    pass
