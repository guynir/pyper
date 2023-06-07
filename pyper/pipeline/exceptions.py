class MissingRequirementsException(Exception):
    """
    This exception, when raised, indicates that a property is missing before a command execution or a command did
    not set a property after execution completes.
    """

    def __init__(self, message: str):
        self.message = message


class AbortPipeline(Exception):
    """
    When called within a Command.handle(), the pipeline aborts operation gracefully.
    """
