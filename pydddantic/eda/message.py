from abc import ABC

from ..value_object import ValueObject


class Message(ValueObject, ABC):
    """
    Abstract base class for a Domain Message, such as a Command or an Event.
    NOTE: This class is not meant to be subclassed directly by your project.
    """

    ...
