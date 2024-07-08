from typing_extensions import Callable, TypeVar

from ..value import Value
from .message import Message

TMessage = TypeVar("TMessage", bound=Message)


class Subscriber(Value[Callable[[TMessage], None]]):
    """
    Create a Domain Message Subscriber to handle a specific type of Domain Message. The Message type is specified via
    the Generic parameter. If a base Message type is used, the Subscriber will also handle any subtype of that Message.

    If a Generic parameter is not provided, a RuntimeError will be raised when the Message Bus encounters the
    Subscriber.

    Example:
        ```
        def on_user_created(event: UserCreatedEvent) -> None:
            print(f"User created: {event}")

        with MessageBus().subscribe(Subscriber[UserCreatedEvent](on_user_created)):
            MessageBus().publish(UserCreatedEvent(id=uuid4(), name="Alice"))
        ```
    """

    def _handle(self, message: TMessage) -> None:
        self.root(message)
