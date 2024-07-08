import threading
from typing_extensions import Self

from .message import Message
from .subscriber import Subscriber


class MessageBus:
    """
    A thread-local Message Bus for publishing and subscribing to Domain Messages. All created instances share
    the same subscribers.

    This bus is not designed for any kind of concurrency, only one handler runs at a time. The goal isn't to
    enable parallelization, but rather to separate tasks conceptually in order to help enforce the Single
    Responsibility Principle enable Eventual Consistency between Aggregates and/or Contexts.

    Example:
        ```
        def on_user_created(event: UserCreatedEvent) -> None:
            print(f"User created: {event}")

        with MessageBus().subscribe(Subscriber[UserCreatedEvent](on_user_created)):
            MessageBus().publish(UserCreatedEvent(id=uuid4(), name="Alice"))
        ```
    """

    __local = threading.local()

    @property
    def __subscribers(self) -> list[Subscriber]:
        if not hasattr(self.__local, "subscribers"):
            self.__local.subscribers = []
        return self.__local.subscribers

    @property
    def __publishing(self) -> bool:
        if not hasattr(self.__local, "publishing"):
            self.__local.publishing = False
        return self.__local.publishing

    @__publishing.setter
    def __publishing(self, value: bool) -> None:
        self.__local.publishing = value

    def publish(self, message: Message) -> None:
        """
        Publish a message to the Event Bus.

        Args:
            message (Message): A subclass of Event or Command to publish for subscribers to handle.

        Raises:
            RuntimeError: Occurs if an invalid subscriber is found.
        """

        if self.__publishing:
            # TODO: What should we do here?
            return

        try:
            self.__publishing = True

            for subscriber in self.__subscribers:
                if (
                    not hasattr(subscriber, "__pydantic_generic_metadata__")
                    or not subscriber.__pydantic_generic_metadata__["args"]
                ):
                    # TODO: Custom exception
                    raise RuntimeError(
                        f"Subscriber {subscriber} is missing a generic type annotation for the event type it handles."
                    )

                if isinstance(message, subscriber.__pydantic_generic_metadata__["args"]):
                    subscriber._handle(message)

        finally:
            self.__publishing = False

    def subscribe(self, *subscriber: Subscriber) -> Self:
        """
        Subscribe to messages published to the Event Bus.

        Example:
            MessageBus().subscribe(
                Subscriber[UserCreated](self.__on_user_created),
                Subscriber[UserUpdated](self.__on_user_updated),
            )

        Returns:
            Self: Returns the instance of the MessageBus to allow for chaining.
        """

        if not self.__publishing:
            self.__subscribers.extend(subscriber)
        return self

    def reset(self) -> Self:
        """
        Clears all subscribers from the Event Bus.

        Returns:
            Self: Returns the instance of the MessageBus to allow for chaining.
        """

        if not self.__publishing:
            self.__subscribers.clear()
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.reset()
