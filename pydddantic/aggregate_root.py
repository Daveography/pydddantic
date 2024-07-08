from abc import ABC
from .entity import Entity


class AggregateRoot(Entity, ABC):
    """
    Abstract base class for an Aggregate Root. This class offers no special functionality on top of Entity,
    it is mostly just to identify Aggregate instances in your domain model.

    When re-typing your Aggregate class' id field, use the IdField annotation to ensure it remains immutable.

    Example:
        ```
        from typing_extensions import Annotated

        class User(AggregateRoot):
            id: Annotated[UUID, AggregateRoot.IdField]
        ```
    """

    ...
