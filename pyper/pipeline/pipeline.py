from typing import Generic, List, Set, Optional, TypeVar

from pyper.exceptions import IllegalStateError
from .callbacks import LifecycleAware
from .command import Command
from .context import CTX, PipelineContextProvider
from .exceptions import MissingRequirementsException, AbortPipeline
from .sink import Sink
from .source import Source

# Pipeline execution results.
PIPE_R = TypeVar("PIPE_R")


class OneTimeSource(Source[CTX]):
    """
    A data source used as a synthetic when no actual data source is provided.
    """

    def __init__(self):
        super().__init__()

        # Counts the number of times this source was used.
        self._count: int = 0

    def setup(self):
        self._count = 0

    def next(self, context: CTX) -> bool:
        """
        Will return 'True' on the first call. Afterward will always return 'False'.
        :param context: Not used.
        :return: 'True' on the first call, then, always 'False'.
        """
        self._count += 1
        return self._count == 1


class Pipeline(Generic[CTX]):

    def __init__(self, source: Source = None,
                 sink: Sink = None,
                 context_provider: PipelineContextProvider = PipelineContextProvider()):
        """
        Class initializer.

        :param source: Optional source that pumps data into the pipeline.
        :param sink: A collector of data called after all commands to extract results.
        """

        # Optional pipeline source.
        self._source: Source = source if source else OneTimeSource()

        # Optional pipeline sink.
        self._sink: Sink = sink

        # Context provider (factory).
        self._context_provider: PipelineContextProvider = context_provider

        # List of commands to execute on every cycle.
        self._commands: List[Command[CTX]] = []

        # Requirements provided by all existing commands.
        self._available_requirements: Set[str] = set()

        # Holds all the objects we need to inform during setup/cleanup phases, typically -- source, sink and commands.
        self._callbacks: List[LifecycleAware] = []

        # If our source is defined, add it to the list of callback-aware objects and extract its list of requirements
        # it may provide.
        if self._source:
            self._available_requirements.update(self._source.provides)
            self._callbacks.append(self._source)

        # If our sink is defined, add it to the list of callback-aware objects. We'll notify it before pipeline
        # execution and after it's done.
        if self._sink:
            self._callbacks.append(self._sink)

    def add_command(self, command: Command[CTX]):
        """
        Add a new command to the pipeline.

        :param command: Command to add.
        :raises MissingRequirementsException: If the command has a requirement that is not fulfilled by previously
        added command.
        """

        requirements: Set[str] = command.requires - self._available_requirements
        if len(requirements) > 0:
            raise MissingRequirementsException(
                f"Command '{command.__class__.__name__}' has unfulfilled requirement(s): '{','.join(requirements)}'.")

        self._commands.append(command)
        self._available_requirements.update(command.provides)

        self._callbacks.append(command)

    def run(self) -> Optional[PIPE_R]:
        """
        Execute a pipeline:
            - Execute setup lifecycle callback to all objects.
            - Pull data from the data source.
            - Execute the commands - one by one.
            - Execute cleanup lifecycle callback to all objects.

        :return: Optionally, a result, if a Sink was defined.
        """

        # Before pipeline execution begins, issue setup callbacks on all objects.
        self._issue_setup_callback()

        try:
            context: CTX = self._context_provider.create_context()

            while self._source.next(context):
                # Call commands.
                for cmd in self._commands:
                    cmd_name: str = cmd.__class__.__name__

                    results: bool = cmd.handle(context)
                    if results is not None and not isinstance(results, bool):
                        raise IllegalStateError(f"Command {cmd_name} returned an unexpected results (type: "
                                                f"{type(results)}). Expected either bool or None.")

                    # If the last command returned 'False', we need to skip the rest of the commands in this cycle.
                    if not results:
                        break

                    # Make sure that this command fulfills all requirements.
                    undefined_properties: Set[str] = set(
                        [prop_name for prop_name in cmd.provides if not context.has_attribute(prop_name)])
                    if len(undefined_properties) > 0:
                        raise MissingRequirementsException(f"Command {cmd.__class__.__name__} did not fulfill all "
                                                           f"requirements (missing: {','.join(undefined_properties)}).")

                if self._sink:
                    self._sink.handle(context)

        except AbortPipeline:
            # In case a command raised 'AbortPipeline' -- we are terminating gracefully and returning nothing to the
            # pipeline caller.
            return None

        finally:
            # After all cycles are done, issue cleanup callbacks.
            self._issue_cleanup_callback()

        return self._sink.get_result() if self._sink else None

    def _issue_setup_callback(self):
        """
        Call setup callback for all listeners.
        """
        for c in self._callbacks:
            c.setup()

    # noinspection PyBroadException
    def _issue_cleanup_callback(self):
        """
        Call cleanup callbacks for all listeners. If any callback raises exception, this exception is silently
        ignored.
        """
        for c in self._callbacks:
            try:
                c.cleanup()
            except BaseException:
                # We ignore all types of exceptions here, so we can issue cleanup callbacks for all listeners.
                pass
