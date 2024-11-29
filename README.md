# pyDDDantic <!-- omit from toc -->

A Pydantic-Based Domain-Driven Design Framework

# Table of Contents <!-- omit from toc -->

- [Introduction](#introduction)
- [Installation](#installation)
- [Base Classes](#base-classes)
  - [`ValueObject`](#valueobject)
  - [`Value`](#value)
  - [`Entity`](#entity)
  - [`AggregateRoot`](#aggregateroot)
  - [Additional Classes](#additional-classes)
    - [`UniqueId`](#UniqueId)
    - [`ImmutableEntity`](#immutableentity)
  - [Serialization](#serialization)
- [Event-Driven Architecture](#event-driven-architecture)
  - [`Message`, `Command`, and `Event`](#message-command-and-event)
  - [`Subscriber`](#subscriber)
  - [`MessageBus`](#messagebus)
- [Aggregates \& Event Sourcing (A+ES)](#aggregates--event-sourcing-aes)
  - [`EventSourcedAggregate`](#eventsourcedaggregate)
- [Sources and Credits](#sources-and-credits)

# Introduction

[Pydantic](pydantic.dev) introduces itself as a data validation library first and foremost. However, with some minor finagling, it can also be a powerful tool for building rich Domain Models following Domain-Driven Design principles.

Note that this documentation does not go into detail about Domain Driven Design concepts or other software patterns and practices. Please see the [Sources and Credits](#sources-and-credits) section for more resources on these concepts.

*This project is not affiliated with Pydantic.*

# Installation

TBD

# Base Classes

This library provides several base classes for implementing your Domain Model.

These classes are subclassed from [pydantic Models](https://docs.pydantic.dev/dev/concepts/models/) and therefore benefit from the built-in validation and serialization features of that library.

## `ValueObject`

Value Objects are subclassed from pydantic `BaseModel`, and thus support the built-in model schema definition.

```python
from pydantic import Field
from pydddantic import ValueObject

class BirdName(ValueObject):
    common_name: str
    scientific_name: str
    other_names: list[str] = Field(default_factory=list)

magpie = BirdName(
    common_name="Black-billed Magpie",
    scientific_name="Pica hudsonia",
    other_names=["Urraca de Hudson", "Pie d'Amérique"],
)

print(magpie)
"""
common_name='Black-billed Magpie' scientific_name='Pica hudsonia' other_names=['Urraca de Hudson', "Pie d'Amérique"]
"""
```

Value Objects are immutable (*frozen*) and cannot be modified:

```python
from pydantic import ValidationError

try:
    magpie.common_name = "Black-billed Jerkface"
except ValidationError as e:
    print(e)
    """
    1 validation error for BirdName
    common_name
    Instance is frozen [type=frozen_instance, input_value='Black-billed Jerkface', input_type=str]   
        For further information visit https://errors.pydantic.dev/2.7/v/frozen_instance
    """
```

Two Value Object instances of the same class with the same data are considered equivalent:

```python
class BirdBehaviour(ValueObject):
    food: str
    behaviour: str

magpie_behaviour = BirdBehaviour(food="Omnivore", behaviour="Ground Forager")

canada_jay_behaviour = BirdBehaviour(food="Omnivore", behaviour="Ground Forager")

print(magpie_behaviour == canada_jay_behaviour)
"""
True
"""
```

## `Value`

Values are simple Value Objects that leverage `RootModel` to hold a single value. This is particularly useful for strong-typing base Python types (like `str`, `int`, etc.) as Value Objects.

```python
from typing_extensions import Annotated
from uuid import UUID, uuid4
from pydantic import StringConstraints
from pydddantic import Value

class BirdId(Value[UUID]): ...

magpie_id = BirdId(uuid4())
print(magpie_id)
"""
c5d51894-939d-4576-9546-e9151e44f408
"""
```

Like `RootModel`, you can add additional validation constraints by annotating the `root` Field:

```python
class BirdFamily(Value[str]):
    root: Annotated[str, StringConstraints(max_length=50, to_upper=True)]

corvidae = BirdFamily("Corvidae")
print(corvidae)
"""
CORVIDAE
"""
```

Value classes are comparable with other Values and values of the same root type:

```python
magpie_family = BirdFamily("CORVIDAE")
canada_jay_family = BirdFamily("CORVIDAE")

print(magpie_family == canada_jay_family)
"""
True
"""

print(canada_jay_family == "CORVIDAE")
"""
True
"""

class IncubationDays(Value[int]): ...

class NestingDays(Value[int]): ...

incubation_time = IncubationDays(12)
nesting_time = NestingDays(12)

print(incubation_time == nesting_time)
"""
True
"""
```

## `Entity`

Entities are Domain Objects that have an identity (`id` field). They can be composed of Values, Value Objects, and other Entities.

```python
from typing_extensions import Annotated
from uuid import UUID, uuid4
from pydantic import Field, StringConstraints
from pydddantic import Entity, Value, ValueObject

class BirdId(Value[UUID]): ...

class BirdName(ValueObject):
    common_name: str
    scientific_name: str
    other_names: list[str] = Field(default_factory=list)

class BirdFamily(Value[str]):
    root: Annotated[str, StringConstraints(max_length=50, to_upper=True)]

class Bird(Entity):
    # Use the following annotation when re-typing the Id field to ensure it remains immutable
    id: Annotated[BirdId, Entity.IdField]
    name: BirdName
    family: BirdFamily

magpie = Bird(
    id=BirdId(uuid4()),
    name=BirdName(
        common_name="Black-billed Magpie",
        scientific_name="Pica hudsonia",
        other_names=["Urraca de Hudson", "Pie d'Amérique"],
    ),
    family=BirdFamily("Corvidae"),
)
print(magpie)
"""
id=BirdId(root=UUID('cfc0ec96-ce3a-41ac-b652-6bdac6da996b')) name=BirdName(common_name='Black-billed Magpie', scientific_name='Pica hudsonia', other_names=['Urraca de Hudson', "Pie d'Amérique"]) family=BirdFamily(root='CORVIDAE')
"""
```

Entities are mutable, and assignment values are re-validated:

```python
magpie.family = "Jerkfacae"
print(magpie)
"""
id=BirdId(root=UUID('e3ef638e-3f18-4792-81e5-a605f1b5acf8')) name=BirdName(common_name='Black-billed Magpie', scientific_name='Pica hudsonia', other_names=['Urraca de Hudson', "Pie d'Amérique"]) family=BirdFamily(root='JERKFACAE')
"""

try:
    magpie.family = None
except ValidationError as e:
    print(e)
    """
    1 validation error for Bird
    family
    Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
        For further information visit https://errors.pydantic.dev/2.7/v/string_type
    """
```

Entity Ids, however, should be immutable once set, provided it has been annotated with `Entity.IdField`:

```python
try:
    magpie.id = BirdId(uuid4())
except ValidationError as e:
    print(e)
    """
    1 validation error for Bird
    id
    Field is frozen [type=frozen_field, input_value=BirdId(root=UUID('64776d0...3b5-a871-69987c2c99bf')), input_type=BirdId]
        For further information visit https://errors.pydantic.dev/2.7/v/frozen_field
    """
```

## `AggregateRoot`

This class is simply a subclass of [`Entity`](#entity), but exists to enable easy identification of your Aggregate Root entities.

This example updates the [`Entity`](#entity) example, but makes `Bird` our `AggregateRoot` (and uses [`UniqueId`](#UniqueId)):

```python
from typing_extensions import Annotated
from pydantic import Field, StringConstraints
from pydddantic import AggregateRoot, Entity, UniqueId, Value, ValueObject

class BirdId(UniqueId): ...

class BirdName(ValueObject):
    common_name: str
    scientific_name: str
    other_names: list[str] = Field(default_factory=list)

class BirdFamily(Value[str]):
    root: Annotated[str, StringConstraints(max_length=50, to_upper=True)]

class Bird(AggregateRoot):
    # Use the following annotation when re-typing the Id field to ensure it remains immutable
    id: Annotated[BirdId, AggregateRoot.IdField]
    name: BirdName
    family: BirdFamily

catbird = Bird(
    id=BirdId.generate(),
    name=BirdName(
        common_name="Gray Catbird",
        scientific_name="Dumetella carolinensis",
        other_names=["Pájaro Gato Gris", "Moqueur chat"],
    ),
    family=BirdFamily("Mimidae"),
)
print(catbird)
"""
id=BirdId(root=UUID('3863dee4-1c2c-4eb9-9dfb-e0e9159405aa')) name=BirdName(common_name='Gray Catbird', scientific_name='Dumetella carolinensis', other_names=['Pájaro Gato Gris', 'Moqueur chat']) family=BirdFamily(root='MIMIDAE')
"""
```

## Additional Classes

These classes are not defined by Domain-Driven Design practices, but exist to help in some relatively common use-cases.

### `UniqueId`

A helper class for creating UUID Value Objects that can be instantiated from and compared to strings and `uuid.UUID`, but not other subclasses of `UniqueId` even if they share a value. Implements a `generate()` class method for creating new Ids.

```python
from pydddantic import UniqueId

class BirdId(UniqueId): ...

flicker_id = BirdId.generate()
print(flicker_id)
"""
d8601f81-5eb3-4b14-b391-32bc8ddfc898
"""

magpie_id = BirdId("c5d51894-939d-4576-9546-e9151e44f408")
print(magpie_id)
"""
c5d51894-939d-4576-9546-e9151e44f408
"""

print(magpie_id == "c5d51894-939d-4576-9546-e9151e44f408")
"""
True
"""

class WhaleId(UniqueId): ...
humpback_id = WhaleId("c5d51894-939d-4576-9546-e9151e44f408")
print(humpback_id == magpie_id)
"""
False
"""
```

### `ImmutableEntity`

Though Entities are designed to be mutable, there are cases where you may not want them to be accidentally modified by your application, such as when loading from an external context before being translated into your Domain Model.

For these situations, you can use `ImmutableEntity`:

```python
from uuid import UUID
from pydddantic import ImmutableEntity

class CornellLabBird(ImmutableEntity):
    id: UUID
    source_url: str
    name: str
    scientific_name: str
    order: str
    family: str
    description: str

northern_flicker = cornell.find("Colaptes auratus")

try:
    northern_flicker.id = uuid4()
except ValidationError as e:
    print(e)
    """
    1 validation error for CornellLabBird
    id
    Instance is frozen [type=frozen_instance, input_value=UUID('64776d0...3b5-a871-69987c2c99bf'), input_type=str]   
        For further information visit https://errors.pydantic.dev/2.7/v/frozen_instance
    """
```

## Serialization

Because these classes are all Pydantic-based, model objects can be serialized and deserialized easily:

```python
chickadee = Bird.model_validate_json(
    """
    {
        "id": "e6da46cf-eb8c-47c7-9bed-b2dc7a95f235",
        "name": {
            "common_name": "Black-capped Chickadee",
            "scientific_name": "Poecile atricapillus",
            "other_names": [
                "Carbonero Cabecinegro",
                "Mésange à tête noire"
            ]
        },
        "family": "Paridae"
    }
    """
)

print(chickadee.model_dump())
"""
{'id': UUID('e6da46cf-eb8c-47c7-9bed-b2dc7a95f235'), 'name': {'common_name': 'Black-capped Chickadee', 'scientific_name': 'Poecile atricapillus', 'other_names': ['Carbonero Cabecinegro', 'Mésange à 
tête noire']}, 'family': 'PARIDAE'}
"""
```

# Event-Driven Architecture

This library also provides classes for helping to develop Event-Driven Architectures.

## `Message`, `Command`, and `Event`

These three classes are [`ValueObject`](#valueobject)s that represent Domain Messages, which consist of Domain Events and Domain Commands.

These base classes have no special properties, except `Event` which defines an `occurred_at` Field that is automatically set to the `datetime` that the instance is created, in UTC.

```python
from pydddantic import Event

class BirdMigratedEvent(Event):
    bird_id: BirdId
    start_coordinates: tuple[float, float]
    end_coordinates: tuple[float, float]
```

## `Subscriber`

This [`Value`](#value) class wraps a `Callable` handler for a `Message` type specified by the generic parameter. This handler will be called when this subscriber is subscribed to the [`MessageBus`](#messagebus):

```python
from pydddantic import Subscriber

def on_bird_migrated(event: BirdMigratedEvent):
    print(event)

sub = Subscriber[BirdMigratedEvent](on_bird_migrated)
```

Subscribing to a base class subscribes to all Messages derived from that base:

```python
from pydddantic import MessageBus

class BirdActivity(Event):
    bird_id: BirdId

class BirdMigratedEvent(BirdActivity):
    start_coordinates: tuple[float, float]
    end_coordinates: tuple[float, float]

class NestBuiltEvent(BirdActivity):
    coordinates: tuple[float, float]
    nest_type: str

def on_bird_activity(event: BirdActivity):
    print(event)

sub = Subscriber[BirdActivity](on_bird_activity)
```

## `MessageBus`

This is a thread-local Pub/Sub Message Bus that your Domain objects can publish to, in order to allow Subscribers in other Contexts react to those Messages.

All instances of `MessageBus` created within the same thread share a list of subscribers.

**NOTE:** This Message Bus is not designed for concurrency; only one handler runs at a time. The goal isn't parallelization, but to separate tasks conceptually in order to help enforce the Single Responsibility Principle and enable Eventual Consistency between Aggregates and/or Contexts.

```python
class BirdActivity(Event):
    bird_id: BirdId

class BirdMigratedEvent(BirdActivity):
    start_coordinates: tuple[float, float]
    end_coordinates: tuple[float, float]

class NestBuiltEvent(BirdActivity):
    coordinates: tuple[float, float]
    nest_type: str

def on_bird_migrated(event: BirdMigratedEvent):
    print(f"Bird {event.bird_id} has migrated! They started at {event.start_coordinates} and flew all the way to {event.end_coordinates}!")

def on_nest_built(event: NestBuiltEvent):
    print(f"Bird {event.bird_id} made a {event.nest_type} nest! It's at {event.coordinates}.")

MessageBus().subscribe(
    Subscriber[BirdMigratedEvent](on_bird_migrated),
    Subscriber[NestBuiltEvent](on_nest_built)
)

MessageBus().publish(
    BirdMigratedEvent(
        bird_id=BirdId("a2094748-37ce-4580-899a-fe36f47eb402"),
        start_coordinates=(30.767139, -94.585373),
        end_coordinates=(53.631625, -112.898750),
    )
)
"""
Bird a2094748-37ce-4580-899a-fe36f47eb402 has migrated! They started at (30.767139, -94.585373) and flew all the way to (53.631625, -112.89875)!
"""

MessageBus().publish(
    NestBuiltEvent(
        bird_id=BirdId("a2094748-37ce-4580-899a-fe36f47eb402"),
        coordinates=(53.631625, -112.898750),
        nest_type="shrub",
    )
)
"""
Bird a2094748-37ce-4580-899a-fe36f47eb402 made a shrub nest! It's at (53.631625, -112.89875).
"""
```

Subscribers can be cleared by resetting the Message Bus:

```python
MessageBus().reset()

MessageBus().publish(
    NestBuiltEvent(
        bird_id=BirdId("a2094748-37ce-4580-899a-fe36f47eb402"),
        coordinates=(53.631625, -112.898750),
        nest_type="shrub",
    )
)
# No output
```

You can also use a context block, after which the subscribers are automatically reset:

```python
with MessageBus().subscribe(
    Subscriber[BirdMigratedEvent](on_bird_migrated),
    Subscriber[NestBuiltEvent](on_nest_built)
):
    MessageBus().publish(
        BirdMigratedEvent(
            bird_id=BirdId("a2094748-37ce-4580-899a-fe36f47eb402"),
            start_coordinates=(30.767139, -94.585373),
            end_coordinates=(53.631625, -112.898750),
        )
    )
    """
    Bird a2094748-37ce-4580-899a-fe36f47eb402 has migrated! They started at (30.767139, -94.585373) and flew all the way to (53.631625, -112.89875)!
    """

MessageBus().publish(
    NestBuiltEvent(
        bird_id=BirdId("a2094748-37ce-4580-899a-fe36f47eb402"),
        coordinates=(53.631625, -112.898750),
        nest_type="shrub",
    )
)
# No output
```

Calls to the Message Bus methods (except `publish`) can also be chained:
```python
with MessageBus().reset().subscribe(
    Subscriber[BirdMigratedEvent](on_bird_migrated)
) as bus:
    bus.publish(
        BirdMigratedEvent(
            bird_id=BirdId("a2094748-37ce-4580-899a-fe36f47eb402"),
            start_coordinates=(30.767139, -94.585373),
            end_coordinates=(53.631625, -112.898750),
        )
    )
    """
    Bird a2094748-37ce-4580-899a-fe36f47eb402 has migrated! They started at (30.767139, -94.585373) and flew all the way to (53.631625, -112.89875)!
    """
```

# Aggregates & Event Sourcing (A+ES)

This library additionally provides some classes to help develop Event-Sourced Aggregates.

## `EventSourcedAggregate`

This is a base class for an Aggregate whose state will be determined by the sum of events affecting it.

Derived classes must implement:
1. An `id` property that returns the Id of the Aggregate
2. A stub/default `_mutate()` method that accepts an event with a type hint of a base `Event` type, decorated with `@functools.singledispatchmethod`
3. Additional `_mutate()` methods that take events with the type hints of specific implementations of the base `Event` and update the state of the aggregate based on those events, decorated with `@_mutate.register`

Additionally, derived classes should also implement:
1. A `@classmethod` that creates and returns a new Aggregate instance
2. Action methods to perform actions on the Aggregate that will alter its state via Events
3. A state object for the Aggregate (an [`AggregateRoot`](#aggregateroot) is recommended)
   - Since `EventSourcedAggregate` is not based on any Pydantic model classes, the state class can be used to implement validation for the Aggregate

```python
from functools import singledispatchmethod
from typing_extensions import Self
from pydddantic import AggregateRoot, Event, EventSourcedAggregate, MessageBus, UniqueId, Value

# Value Objects
class BirdId(UniqueId): ...

class Coordinates(Value[tuple[float, float]]): ...

# Events
class BirdActivity(Event):
    bird_id: BirdId

class BirdTrackingStartedEvent(BirdActivity):
    coordinates: Coordinates

class BirdMigratedEvent(BirdActivity):
    start_coordinates: Coordinates
    end_coordinates: Coordinates

class NestBuiltEvent(BirdActivity):
    coordinates: Coordinates
    nest_type: str

# State
class _TrackedBirdState(AggregateRoot):
    id: BirdId
    current_coordinates: Coordinates
    nest_coordinates: Coordinates | None = None
    nest_type: str | None = None

# Aggregate
class TrackedBird(EventSourcedAggregate):
    _state: _TrackedBirdState

    @property
    def id(self) -> BirdId:
        return self._state.id

    @property
    def current_coordinates(self) -> Coordinates:
        return self._state.current_coordinates

    @property
    def is_nesting(self) -> bool:
        return self._state.nest_coordinates is not None

    @property
    def nest_coordinates(self) -> Coordinates | None:
        return self._state.nest_coordinates

    @property
    def nest_type(self) -> str | None:
        return self._state.nest_type

    @classmethod
    def start(cls, coordinates: Coordinates) -> Self:
        event = BirdTrackingStartedEvent(bird_id=BirdId.generate(), coordinates=coordinates)
        bird = cls()
        bird._apply(event)
        MessageBus().publish(event)
        return bird

    def migrate(self, new_coordinates: Coordinates) -> None:
        event = BirdMigratedEvent(bird_id=self.id, start_coordinates=self.current_coordinates, end_coordinates=new_coordinates)
        self._apply(event)
        MessageBus().publish(event)

    def nest(self, coordinates: Coordinates, nest_type: str) -> None:
        event = NestBuiltEvent(bird_id=self.id, coordinates=coordinates, nest_type=nest_type)
        self._apply(event)
        MessageBus().publish(event)

    @singledispatchmethod
    def _mutate(self, event: BirdActivity) -> None:
        raise NotImplementedError(f"Unhandled event type '{type(event)}'")

    @_mutate.register
    def _on_tracking_started(self, event: BirdTrackingStartedEvent) -> None:
        self._state = _TrackedBirdState(id=event.bird_id, current_coordinates=event.coordinates)

    @_mutate.register
    def _on_bird_migrated(self, event: BirdMigratedEvent) -> None:
        self._state.current_coordinates = event.end_coordinates

    @_mutate.register
    def _on_nest_built(self, event: NestBuiltEvent) -> None:
        self._state.nest_coordinates = event.coordinates
        self._state.nest_type = event.nest_type

my_bird = TrackedBird.start(coordinates=(30.767139, -94.585373))
print(my_bird._state)
"""
id=BirdId(root=UUID('426ba7dc-78f7-4bfa-9fd2-2d7fdcc2d8e6')) current_coordinates=Coordinates(root=(30.767139, -94.585373)) nest_coordinates=None nest_type=None
"""

my_bird.migrate(new_coordinates=(53.631625, -112.898750))
print(my_bird._state)
"""
id=BirdId(root=UUID('426ba7dc-78f7-4bfa-9fd2-2d7fdcc2d8e6')) current_coordinates=Coordinates(root=(53.631625, -112.89875)) nest_coordinates=None nest_type=None
"""

my_bird.nest(coordinates=(53.631625, -112.898750), nest_type="shrub")
print(my_bird._state)
"""
print(my_bird._state)
id=BirdId(root=UUID('426ba7dc-78f7-4bfa-9fd2-2d7fdcc2d8e6')) current_coordinates=Coordinates(root=(53.631625, -112.89875)) nest_coordinates=Coordinates(root=(53.631625, -112.89875)) nest_type='shrub'
"""
```

# Sources and Credits

- Eric Evans ([Domain-Driven Design: Tackling Complexity in the Heart of Software](https://www.dddcommunity.org/book/evans_2003/))
- Vaughn Vernon ([Implementing Domain-Driven Design](https://www.dddcommunity.org/book/implementing-domain-driven-design-by-vaughn-vernon/))
- Harry J.W. Percival & Bob Gregory ([Architecture Patterns with Python](https://www.cosmicpython.com/))