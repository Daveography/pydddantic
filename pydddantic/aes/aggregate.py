from abc import ABC, abstractmethod
from collections.abc import Sequence
from functools import singledispatchmethod
from typing_extensions import Any

from ..eda.event import Event
from .stream import EventStream


class EventSourcedAggregate(ABC):
    """
    Abstract base class for an Event-Sourced Aggregate when using Aggregate + Event Sourcing (A+ES).

    Subclasses must implement _mutate as singledispatchmethods for each event type they handle.
    """

    def __init__(self, event_stream: EventStream | None = None) -> None:
        """
        Creates the Aggregate from a sequence of Domain Events, such as when loading from an Event Store.

        Args:
            event_stream (EventStream | None, optional):
                The Event Stream from which to load the Aggregate. May be None to create a new Aggregate.
                Defaults to None.
        """

        self.__changes: list[Event] = []
        self.__version = 0

        if event_stream is not None:
            self.__version = event_stream.version
            for event in event_stream:
                self._mutate(event)

    @property
    @abstractmethod
    def id(self) -> Any:
        "The unique identifier for the Aggregate; must be implemented by the subclass"
        raise NotImplementedError

    @property
    def changes(self) -> Sequence[Event]:
        "A list of mutating events applied to the Aggregate since it was last loaded from the Event Store"
        return self.__changes.copy()

    @property
    def version(self) -> int:
        "The version of the Aggregate at the time it was loaded from the Event Store"
        return self.__version

    @singledispatchmethod
    @abstractmethod
    def _mutate(self, event: Event) -> None:
        """
        Mutate the Aggregate state based on the provided Event. Handlers for specific events should be implemented as
        `singledispatchmethod`s.

        Args:
            event (Event): The event to use to mutate the Aggregate

        Raises:
            NotImplementedError: If not implemented by the subclass

        Example:
            ```
            from functools import singledispatchmethod

            class User(EventSourcedAggregate):
                @singledispatchmethod
                def _mutate(self, event: UserEvent) -> None:
                    raise NotImplementedError

                @_mutate.register
                def _user_created(self, event: UserCreatedEvent) -> None:
                    ...

                @_mutate.register
                def _user_name_changed(self, event: UserNameChangedEvent) -> None:
                    ...
            ```
        """

        raise NotImplementedError

    def _apply(self, event: Event) -> None:
        """
        Apply the provided Event to the Aggregate, updating the state and recording the change for later persistence.

        Args:
            event (Event): The event to apply to the Aggregate
        """

        self.__changes.append(event)
        self._mutate(event)
