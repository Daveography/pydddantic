from __future__ import annotations

from abc import ABC
from typing import Any  # Cannot be imported from typing_extensions when used in a Pydantic model
from typing_extensions import Annotated, ClassVar, Hashable

from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo


class Entity(BaseModel, Hashable, ABC):
    """
    Abstract base class for a Domain Entity using Pydantic's BaseModel. Entities require an identity (id),
    which is used to determine equality and the object hash. Entity fields are always re-validated on assignment.

    When re-typing your Entity class' id field, use the IdField annotation to ensure it remains immutable.

    Example:
        ```
        from typing_extensions import Annotated

        class User(Entity):
            id: Annotated[UUID, Entity.IdField]
        ```
    """

    IdField: ClassVar[FieldInfo] = Field(frozen=True)
    """
    Use this to annotate a re-typed id field to ensure it remains immutable.

    Example:
        `id: Annotated[UUID, Entity.IdField]`
    """

    id: Annotated[Any, Entity.IdField]
    """
    The unique identity of this entity. REQUIRED.

    When re-typing your Entity class' id field, use the IdField annotation to ensure it remains immutable.

    Example:
        `id: Annotated[UUID, Entity.IdField]`
    """

    def __eq__(self, other: Entity) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    model_config = ConfigDict(validate_assignment=True)
