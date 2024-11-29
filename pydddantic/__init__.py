from typing_extensions import deprecated

from .aes import EventSourcedAggregate, EventStore, EventStream
from .aggregate_root import AggregateRoot
from .eda import Command, Event, Message, MessageBus, Subscriber
from .entity import Entity
from .immutable_entity import ImmutableEntity
from .unique_id import UniqueId
from .value import Value
from .value_object import ValueObject


@deprecated("`UUIDValue` is deprecated and will be removed in a future release. Use `UniqueId` instead.")
class UUIDValue(UniqueId):
    pass


__all__ = [
    "AggregateRoot",
    "Command",
    "Event",
    "EventSourcedAggregate",
    "EventStore",
    "EventStream",
    "Entity",
    "ImmutableEntity",
    "Message",
    "MessageBus",
    "Subscriber",
    "UniqueId",
    "UUIDValue",
    "Value",
    "ValueObject",
]
