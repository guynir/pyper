from unittest import TestCase

from pyper.pipeline import *
from pyper.pipeline.test.pipeline_test_helper import EmptyCommand


class CustomContext(Context):
    """
    Custom context that includes a 'name' property.
    """

    def __init__(self):
        super().__init__()
        self.name = None


class CustomContextProvider(PipelineContextProvider[CustomContext]):
    """
    Context provider for creating 'CustomContext'.
    """

    def create_context(self) -> CustomContext:
        return CustomContext()


class SinkTest(TestCase):

    def test_sink_should_provide_property_value(self):
        """
        Test that a 'Sink' provides a property value from the context.
        """

        value = "Guy"

        # Function called by command's 'handle' method.
        def define_value(ctx: CustomContext):
            ctx.name = value

        # Create and execute a pipeline. Expect the Sink to provide results.
        pipeline = Pipeline(sink=Sink("name"), context_provider=CustomContextProvider())
        pipeline.add_command(EmptyCommand(define_value, provides={"name"}))
        results: str = pipeline.run()

        self.assertEqual(results, value)
