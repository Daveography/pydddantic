from collections.abc import Iterator
from typing_extensions import Generic, TypeVar

from pydantic import NonNegativeInt

from ..eda.event import Event
from ..value_object import ValueObject

TEvent = TypeVar("TEvent", bound=Event)


class EventStream(ValueObject, Generic[TEvent]):
    """
    Value Object holding a stream of loaded events from an Event Store, including the current version.
    """

    version: NonNegativeInt
    "The current version of the Event Stream as obtained by the Event Store. New Aggregates should start with version 0"

    events: list[TEvent]
    "The list of Events loaded from the Event Store. New Aggregates should start with an empty list of events."

    def __iter__(self) -> Iterator[TEvent]:
        return iter(self.events)
