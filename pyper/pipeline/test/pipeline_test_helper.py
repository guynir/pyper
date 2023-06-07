from typing import Callable, Optional, Set

from pyper.pipeline import CTX, Command, Source


class EmptySource(Source[CTX]):

    def __init__(self, next_handler: Callable[[CTX], Optional[bool]] = None, provides: Set[str] = None):
        super().__init__(provides)
        self._next_handler: Callable[[CTX], Optional[bool]] = next_handler

    def next(self, context: CTX) -> bool:
        return self._next_handler if self._next_handler else False


class EmptyCommand(Command[CTX]):
    """ Empty command to use for testing. """

    def __init__(self, handler: Callable[[CTX], Optional[bool]] = None,
                 provides: Set[str] = None,
                 requires: Set[str] = None):
        """
        Class initializer.

        :param handler: Optional handler to be called by handle() method. Maybe None.
        :param provides: Optional set of properties this command provides.
        :param requires: Optional set of properties this command requires.
        """
        super().__init__(provides, requires)
        self._handler: Callable[[CTX], Optional[bool]] = handler

    def handle(self, context: CTX) -> bool:
        return self._handler(context) if self._handler else None
