import unittest
from functools import singledispatchmethod
from typing_extensions import Annotated, Self
from uuid import UUID, uuid4

from pydddantic import AggregateRoot, Event, EventSourcedAggregate, EventStream, MessageBus


class _UserState(AggregateRoot):
    id: Annotated[UUID, AggregateRoot.IdField]
    name: str


class UserEvent(Event):
    id: UUID


class UserCreatedEvent(UserEvent):
    name: str


class UserNameChangedEvent(UserEvent):
    old_name: str
    new_name: str


class User(EventSourcedAggregate):
    __state: _UserState

    @property
    def id(self) -> UUID:
        return self.__state.id

    @property
    def name(self) -> str:
        return self.__state.name

    @classmethod
    def create(cls, name: str) -> Self:
        event = UserCreatedEvent(id=uuid4(), name=name)
        user = cls()
        user._apply(event)
        MessageBus().publish(event)
        return user

    def change_name(self, new_name: str) -> None:
        event = UserNameChangedEvent(id=self.id, old_name=self.name, new_name=new_name)
        self._apply(event)
        MessageBus().publish(event)

    @singledispatchmethod
    def _mutate(self, event: UserEvent) -> None:
        raise NotImplementedError(f"Unhandled event type '{type(event)}'")

    @_mutate.register
    def _user_created(self, event: UserCreatedEvent) -> None:
        self.__state = _UserState(id=event.id, name=event.name)

    @_mutate.register
    def _user_name_changed(self, event: UserNameChangedEvent) -> None:
        self.__state.name = event.new_name


class EventSourcedAggregateTests(unittest.TestCase):
    def test_new_aggregate_version_should_be_zero(self):
        # Given
        user = User.create(name="Alice")

        # Expect
        self.assertEqual(0, user.version)

    def test_should_record_aggregate_state_changes(self):
        # Given
        user = User.create(name="Alice")

        # When
        user.change_name(new_name="Bob")

        # Expect
        self.assertEqual(2, len(user.changes))
        self.assertIsInstance(user.changes[0], UserCreatedEvent)
        self.assertIsInstance(user.changes[1], UserNameChangedEvent)

    def test_should_record_only_state_changes_after_aggregate_loaded(self):
        # Given
        user = User(event_stream=EventStream(version=1, events=[UserCreatedEvent(id=uuid4(), name="Alice")]))

        # When
        user.change_name(new_name="Bob")

        # Expect
        self.assertEqual(1, len(user.changes))
        self.assertIsInstance(user.changes[0], UserNameChangedEvent)

    def test_version_should_be_set_by_event_stream(self):
        # Given
        user = User(event_stream=EventStream(version=4, events=[UserCreatedEvent(id=uuid4(), name="Alice")]))

        # Expect
        self.assertEqual(4, user.version)

    def test_changes_should_return_copy(self):
        # Given
        user = User.create(name="Alice")

        # When
        changes = user.changes

        # Expect
        self.assertIsNot(user.changes, changes)
        self.assertEqual(1, len(changes))
        self.assertEqual(1, len(user.changes))

        # Then
        changes.append(UserNameChangedEvent(id=user.id, old_name="Alice", new_name="Bob"))  # type: ignore

        # Expect
        self.assertEqual(2, len(changes))
        self.assertEqual(1, len(user.changes))
