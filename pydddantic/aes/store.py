from typing_extensions import Any, Protocol

from .aggregate import EventSourcedAggregate
from .stream import EventStream


class EventStore(Protocol):
    """
    Protocol for implementing an Event Store for Event-Sourced Aggregates.
    """

    def load(self, id: Any) -> EventStream:
        """
        Loads an Event Stream from the Event Store for the provided Aggregate Id, which can be used to recreate an
        Event Sourced Aggregate.

        Args:
            id (Any): The Aggregate Id to load

        Returns:
            EventStream: The Event Stream for the Aggregate Id
        """

        ...

    def append(self, aggregate: EventSourcedAggregate) -> None:
        """
        Updates the Event Store with the new Events from the Aggregate.

        Args:
            aggregate (EventSourcedAggregate):
                The Aggregate instance whose changes will be appended to the Event Store
        """

        ...

    def get_version(self, id: Any) -> int:
        """
        Returns the current version of the Event Stream for a given Aggregate Id

        Args:
            id (Any): The Aggregate Id whose version to get

        Returns:
            int: The latest version number of the Aggregate
        """

        ...
