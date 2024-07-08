from abc import ABC
from datetime import datetime, timezone

from pydantic import Field

from .message import Message


class Event(Message, ABC):
    """
    Abstract base class for a Domain Event.
    """

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    "The date and time the event occurred. Defaults to the UTC date and time at which the event is created."
