from abc import ABC, abstractmethod
from typing import Generic, Set, List

from pyper.exceptions import IllegalArgumentError
from pyper.pipeline.callbacks import LifecycleAware
from pyper.pipeline.context import CTX


class Source(ABC, LifecycleAware, Generic[CTX]):
    """
    A source object feeds input to the pipeline.
    """

    def __init__(self, provides: Set[str] = None):
        """
        Class initializer.

        :param provides: Optional list of properties this source provides.
        """
        self._provides = provides if provides is not None else set()

    @property
    def provides(self) -> Set[str]:
        """
        :return: List of properties the source provides.
        """
        return self._provides

    @abstractmethod
    def next(self, context: CTX) -> bool:
        """
        Handle is called by the pipeline to update the context with the next available data. If no more data is
        available, this method should return 'False' to finish pipeline execution.

        :param context: Context to update.
        :return: 'True' if a source provided new data for the pipeline, 'False' if no data is available and the pipeline
        should terminate execution.
        """
        pass


class SimpleListSource(Source[CTX]):
    """
    A simple data source that provides data items from predefined list (passed via initializer).
    """

    def __init__(self, property_name: str, data: List):
        """
        Class initializer.

        :param property_name: Name of property to set data at.
        :param data: List of data items to provide to pipeline.
        """
        super().__init__({property_name})

        # Make sure data is defined and is a list.
        if not data or not isinstance(data, list):
            raise IllegalArgumentError(f"Invalid data type: {type(data)}. Expected a list.")

        # Name of context property that data will be set into.
        self._property_name: str = property_name

        # List of items.
        self._data: List = data

        # Index of current item to copy into context.
        self._index: int = 0

    def setup(self):
        self._index = 0

    def next(self, context: CTX) -> bool:
        """
        Provide the next item on the 'data'.

        :param context: Context to set data into.
        :return: 'True' if data was set or 'False' if no more data is available.
        """
        has_data: bool = self._index < len(self._data)
        if has_data:
            context.set(self._property_name, self._data[self._index])
            self._index += 1

        return has_data
