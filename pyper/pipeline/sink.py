from typing import Set, Optional, Generic

from .callbacks import LifecycleAware
from .context import CTX


class Sink(LifecycleAware, Generic[CTX]):
    """
    A sink is the last step of a pipeline, typically gathering resulting data from the context.
    """

    def __init__(self, result_property_name: Optional[str] = None):
        # Holds the property that
        self._property_name: Optional[str] = result_property_name

        # Set of required properties by this sink.
        # If the caller provided a property representing the result -- declare it as a requirement.
        # Otherwise, this sink has no requirement.
        self._requires = set(result_property_name) if result_property_name is not None else set()

        self._result: Optional[object] = None

    @property
    def requires(self) -> Set[str]:
        return self._requires

    def handle(self, context: CTX):
        # If caller defined a property representing the result, keep it locally for future use.
        if self._property_name:
            self._result = getattr(context, self._property_name)

    def get_result(self) -> object:
        return self._result
