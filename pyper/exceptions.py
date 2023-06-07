class IllegalArgumentError(Exception):
    """
    This exception typically thrown when an invalid argument is passed to a function (such as None instead of actual
    value, or when the type does not match).
    """

    def __init__(self, message: str):
        """
        Class initializer.

        :param message: Error message.
        """
        self._message = message

    @property
    def message(self) -> str:
        """
        :return: Error message embedded in this exception.
        """
        return self._message


class IllegalStateError(Exception):
    """
    This exception typically thrown when an unexpected state is encountered.
    """

    def __init__(self, message: str):
        """
        Class initializer.

        :param message: Error message.
        """
        self._message = message

    @property
    def message(self) -> str:
        """
        :return: Error message embedded in this exception.
        """
        return self._message
