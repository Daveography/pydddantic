import unittest
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from pydddantic.eda import Event, MessageBus, Subscriber


class UserEvent(Event):
    id: UUID


class UserCreatedEvent(UserEvent):
    name: str


class UserNameChangedEvent(UserEvent):
    old_name: str
    new_name: str


class MessageBusTests(unittest.TestCase):
    def test_should_receive_subscribed_event(self):
        # Given
        mock_subscriber = MagicMock()

        with MessageBus().subscribe(Subscriber[UserCreatedEvent](mock_subscriber.on_user_created)):

            # When
            MessageBus().publish(UserCreatedEvent(id=uuid4(), name="Alice"))

        # Expect
        mock_subscriber.on_user_created.assert_called_once()

    def test_should_receive_all_events_derived_from_subscribed_base_event(self):
        # Given
        mock_subscriber = MagicMock()
        id = uuid4()

        with MessageBus().subscribe(Subscriber[UserEvent](mock_subscriber.on_any_user_event)):

            # When
            MessageBus().publish(UserCreatedEvent(id=id, name="Alice"))
            MessageBus().publish(UserNameChangedEvent(id=id, old_name="Alice", new_name="Bob"))

        # Expect
        mock_subscriber.on_any_user_event.assert_called()
        self.assertEqual(2, mock_subscriber.on_any_user_event.call_count)

    def test_should_not_receive_events_not_subscribed_to(self):
        # Given
        mock_subscriber = MagicMock()

        with MessageBus().subscribe(Subscriber[UserCreatedEvent](mock_subscriber.on_user_created)):

            # When
            MessageBus().publish(UserNameChangedEvent(id=uuid4(), old_name="Alice", new_name="Bob"))

        # Expect
        mock_subscriber.on_user_created.assert_not_called()

    def test_should_raise_if_subscription_missing_generic_param_for_event_type(self):
        # Given
        mock_subscriber = MagicMock()

        with MessageBus().subscribe(Subscriber(mock_subscriber.on_any_event)):

            # Expect
            with self.assertRaises(RuntimeError):
                MessageBus().publish(UserCreatedEvent(id=uuid4(), name="Alice"))

    def test_reset_should_clear_subscribers(self):
        # Given
        mock_subscriber = MagicMock()
        id = uuid4()

        MessageBus().subscribe(
            Subscriber[UserCreatedEvent](mock_subscriber.on_user_created),
            Subscriber[UserNameChangedEvent](mock_subscriber.on_user_name_changed),
        )

        MessageBus().publish(UserCreatedEvent(id=id, name="Alice"))

        # When
        MessageBus().reset()
        MessageBus().publish(UserNameChangedEvent(id=id, old_name="Alice", new_name="Bob"))

        # Expect
        mock_subscriber.on_user_created.assert_called_once()
        mock_subscriber.on_user_name_changed.assert_not_called()

    def test_should_clear_subscribers_on_exiting_with_block(self):
        # Given
        mock_subscriber = MagicMock()
        id = uuid4()

        with MessageBus().subscribe(
            Subscriber[UserCreatedEvent](mock_subscriber.on_user_created),
            Subscriber[UserNameChangedEvent](mock_subscriber.on_user_name_changed),
        ):
            MessageBus().publish(UserCreatedEvent(id=id, name="Alice"))

        # When
        MessageBus().publish(UserNameChangedEvent(id=id, old_name="Alice", new_name="Bob"))

        # Expect
        mock_subscriber.on_user_created.assert_called_once()
        mock_subscriber.on_user_name_changed.assert_not_called()
