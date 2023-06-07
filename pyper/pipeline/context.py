from typing import TypeVar, Optional, Dict, Generic

PV = TypeVar("PV")


class Context:
    """
    A context maintains the state of pipeline execution. Each time a pipeline is executed, a new context is created
    to share the state among the various steps (commands).

    Most specific pipeline commands will require a specific type of context inherited from this one. For example, a
    pipeline that compress files will require a specific context (e.g.: FileCompressionContext) that will have
    properties specific for file locations or file list.

    A context is composed of properties (set of pre-defined fields, defined within the '__init__') and attributes,
    which are free-style values maintained in a dictionary.
    """

    def __init__(self):
        """
        Class initializer.
        """

        # Maintains context's attributes.
        self._attributes: Dict[str, object] = {}

    def get(self, attribute_name: str, fallback_value: Optional[PV] = None) -> Optional[PV]:
        """
        Retrieve an attribute.

        :param attribute_name: Attribute name.
        :param fallback_value:  Optional fallback value, in-case attribute was not set. Defaults to 'None'.
        :return: Attribute value, which may be 'None'.
        """
        return self._attributes.setdefault(attribute_name, fallback_value)

    def set(self, attribute_name: str, attribute_value: any):
        """
        Sets an attribute value.

        :param attribute_name: Attribute name.
        :param attribute_value:  Attribute value.
        """
        self._attributes[attribute_name] = attribute_value

    def is_property_defined(self, property_name: str) -> bool:
        """
        Check if a given property within this context has a non-None value.

        :param property_name: Property name.
        :return: True if property has a non-None value, otherwise - False. If property is not defined, this call
        will return False.
        """
        return hasattr(self, property_name) and getattr(self, property_name) is not None


CTX = TypeVar("CTX", bound=Context)


class PipelineContextProvider(Generic[CTX]):
    """
    A factory called before every pipeline cycle to create a new Context object. Allows a pipeline user to
    configure how a context is created and configured.
    """

    # noinspection PyMethodMayBeStatic
    def create_context(self) -> CTX:
        """
        Creates a new Context object.
        :return: A new Context object on every call.
        """
        return Context()






