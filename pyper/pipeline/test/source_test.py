from typing import List
from unittest import TestCase

from pyper.pipeline import *
from pyper.pipeline.source import SimpleListSource


class CustomContext(Context):

    def __init__(self):
        super().__init__()
        self.total: int = 0


class CustomContextProvider(PipelineContextProvider):

    def create_context(self) -> CTX:
        return CustomContext()


class SumCommand(Command):
    """
    A command that sums all values provided by source.
    """

    def __init__(self):
        super().__init__()
        self._total: int = 0

    def handle(self, context: CustomContext) -> bool:
        self._total += context.get("value")
        context.total = self._total
        return True


class SourceTest(TestCase):

    def test_should_iterate_over_all_source_values(self):
        """
        Test that a data source provides all values to pipeline.
        """
        value_list: List[int] = [1, 3, 8, 9]

        # A simple/mock data source that provides predefined values.
        source = SimpleListSource("value", value_list)

        # Create a pipeline and execute it.
        pipeline = Pipeline(source, Sink("total"), CustomContextProvider())
        pipeline.add_command(SumCommand())
        results: int = pipeline.run()

        self.assertEqual(sum(value_list), results)
