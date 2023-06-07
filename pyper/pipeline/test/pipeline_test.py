from unittest import TestCase
from unittest.mock import MagicMock

from pyper.pipeline import *
from pyper.pipeline.test.pipeline_test_helper import EmptyCommand, EmptySource


# noinspection PyMethodMayBeStatic
class PipelineTest(TestCase):

    def test_should_call_command_handle_method_once(self):
        """
        Test that for a simple pipeline (with no data source), a command is called exactly once.
        """

        command = EmptyCommand()
        command.handle = MagicMock(return_value=None)
        pipeline = Pipeline()
        pipeline.add_command(command)
        pipeline.run()

        command.handle.assert_called_once()

    def test_should_issue_callbacks(self):
        """
        Test that setup and cleanup callbacks are issued on Source, Sink and Command objects.
        """

        # Create our test objects.
        source = EmptySource()
        sink = Sink()
        command = EmptyCommand()

        # Make setup/cleanup mock methods, so we can evaluate if they were called.
        source.setup = MagicMock()
        source.cleanup = MagicMock()
        sink.setup = MagicMock()
        sink.cleanup = MagicMock()
        command.setup = MagicMock()
        command.cleanup = MagicMock()

        # Create a pipeline and execute it.
        pipeline = Pipeline(source, sink)
        pipeline.add_command(command)
        pipeline.run()

        # Make sure our lifecycle setup/clean callbacks were issued on all objects.
        source.setup.assert_called()
        source.cleanup.assert_called()
        sink.setup.assert_called()
        sink.cleanup.assert_called()
        command.setup.assert_called()
        command.cleanup.assert_called()

    def test_should_not_issue_commands_after_skip_command(self):
        """
        Test that when a command returns 'False' on a call to 'handle()', the next commands in the pipeline
        are skipped (such a command is called 'Skip command').
        """
        cmd1 = EmptyCommand()
        cmd2 = EmptyCommand()
        cmd1.handle = MagicMock(return_value=False)
        cmd2.handle = MagicMock(return_value=False)

        # Create a pipeline with a skip-command.
        pipeline = Pipeline()
        pipeline.add_command(cmd1)
        pipeline.add_command(cmd2)
        pipeline.run()

        # Make sure command1 was called while the next command was skipped.
        cmd1.handle.assert_called_once()
        cmd2.handle.assert_not_called()

    def test_should_invoke_cleanups_even_on_error(self):
        """
        Test should cause a command to break pipeline execution but make sure that 'cleanup'
        nevertheless.
        """

        # noinspection PyUnusedLocal
        # Function that raises exception when 'handle' method is called.
        def error(ctx):
            raise EnvironmentError()

        # Define two commands that at least one raises an exception.
        cmd1 = EmptyCommand(error)
        cmd1.cleanup = MagicMock()
        cmd2 = EmptyCommand()
        cmd2.cleanup = MagicMock()

        # Create a pipeline and execute it.
        pipeline = Pipeline()
        pipeline.add_command(cmd1)
        pipeline.add_command(cmd2)
        try:
            # cmd1 should raise an exception when 'handle()' method is called.
            pipeline.run()
        except EnvironmentError:
            pass

        # Make sure that although cmd1 raised an exception during execution, all commands
        # lifecycle methods we issued.
        cmd1.cleanup.assert_called_once()
        cmd2.cleanup.assert_called_once()

    def test_should_provide_requirements_to_command(self):
        """
        Test that prior command(s) fulfills a requirements by later command(s).
        """
        providing_cmd = EmptyCommand(provides={"name"})
        requiring_cmd = EmptyCommand(requires={"name"})

        # Create a pipeline and add commands.
        # Upon adding, the pipeline makes sure that all requirements by 'requiring_cmd' are fulfilled by
        # 'providing_cmd'.
        pipeline = Pipeline()
        pipeline.add_command(providing_cmd)
        pipeline.add_command(requiring_cmd)

    def test_should_fail_on_missing_requirement(self):
        """
        Test that a command with requirement not fulfilled generates an exception.
        """

        requiring_cmd = EmptyCommand(requires={"name"})

        # Trying to add a command with an unfulfilled requirement should result in an exception.
        with self.assertRaises(MissingRequirementsException):
            pipeline = Pipeline()
            pipeline.add_command(requiring_cmd)
