from abc import ABC, abstractmethod
from typing import Set, Generic, Optional, Union, List, Tuple

from pyper.pipeline.callbacks import LifecycleAware
from pyper.pipeline.context import CTX, Context
from pyper.pipeline.exceptions import MissingRequirementsException
from pyper.pipeline.utils import to_set


class Command(ABC, LifecycleAware, Generic[CTX]):
    """
    A command is an execution code which is part of the pipeline chain. Each command executed is responsible for
    a specific task. For example, in a file compression pipeline, one command can be responsible for reading
    data into the context while another command will be responsible for compressing it. Eventually, a further command
    may write it to a destination storage.

    A command has several life-cycle stages. Firstly, a 'setup' method is called before the pipeline is executed.
    Following that, each pipeline cycle will invoke the 'handle' method.
    Finally, when pipeline execution completes (whether gracefully or not), the 'cleanup' callback is invoked.

    A command is typically designated to a specific context type (hence the generics of this class). For example, a
    file-compression pipeline command may require a FileCompressionContext instance that will contain all the
    properties required to execute the task.

    Each command declares a set of properties it sets ('provides'), and a set of properties consumes ('requires).
    The pipeline asserts that before each call a command has all required properties set, and after each call, all
    provided properties are defined (not None).
    """

    def __init__(self,
                 provides_properties: Optional[Union[Set, List, Tuple, object]] = None,
                 requires_properties: Optional[Union[Set, List, Tuple, object]] = None):
        """
        Class initializer.
        """

        # Maintains the list of properties this command provides.
        self._provides_properties: Set[str] = to_set(provides_properties)

        # Maintains the list of required properties for this command to execute.
        self._requires_properties: Set[str] = to_set(requires_properties)

    @property
    def provides(self) -> Set[str]:
        """
        :return: The list of properties this command always sets.
        """
        return self._provides_properties

    @property
    def requires(self) -> Set[str]:
        """
        :return: The list of properties this command always requires prior to execution.
        """
        return self._requires_properties

    @abstractmethod
    def handle(self, context: CTX) -> bool:
        """
        The heart and body of the command - called by the pipeline engine to execute a dedicated job. All
        parameters are passed via the 'context' parameter.

        :param context: Pipeline execution context.
        :return: True if the pipeline should continue the execution chain or False, to skip the rest of the
        commands.
        :raises StopIteration: If this command wishes to abort the pipeline execution gracefully.
        """
        pass

    def _invoke(self, context: CTX) -> bool:
        """
        Called internally by the pipeline engine. This method is a wrap-around the 'handle' method to perform
        pre- / post-operations before/after 'handle' is executed.
        :param context: Pipeline execution context.

        :return: True if the pipeline should continue the execution chain or False, to skip the rest of the
        commands.
        """

        # Make sure all requirements are available prior to command execution.
        self.__assert_requirements(self.requires, context,
                                   "Missing the following requirements for command '{cmd_name}': {requirements}")

        # Execute command.
        result = self.handle(context)

        # If a command declared list of properties it must set, make sure all are defined after execution.
        if len(self.provides) > 0:
            self.__assert_requirements(self.provides, context,
                                       "Command {cmd_name} did not set the following requirements: {requirements}.")

        return result if result is not None else True

    def __assert_requirements(self, requirements: Set[str], context: Context, message: str):
        """
        Make sure that a given set of requirements are defined/set within the context.

        :param requirements: List of requirements.
        :param context:  Context to examine.
        :param message: Error message to set for exception if one or more requirements are missing.
        :raises MissingRequirementsException: If one or more requirements are missing from context.
        """
        missing_requirements: Set[str] = set(
            [req for req in requirements if not context.has_attribute(req)])

        if len(missing_requirements) > 0:
            raise MissingRequirementsException(
                message.format(cmd_name=self.__class__.__name__, requirements=missing_requirements))
