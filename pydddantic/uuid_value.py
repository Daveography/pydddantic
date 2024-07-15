from abc import ABC
from typing_extensions import Annotated, Self
from uuid import UUID, uuid4
from pydantic import BeforeValidator

from .value import Value


class UUIDValue(Value[UUID], ABC):
    """
    Abstract base class for a UUID Value Object. Implements a `generate()` class method to generate a new Id.
    """

    root: Annotated[str | UUID, BeforeValidator(lambda v: UUID(v) if not isinstance(v, UUID) else v)]

    @classmethod
    def generate(cls) -> Self:
        """
        Generate a new UUID Value Object.

        Returns:
            Self: A UUID Value Object
        """
        return cls(uuid4())

    def __eq__(self, other: str | UUID | Value[UUID]) -> bool:
        if isinstance(other, Value):
            return self.root == other.root
        if isinstance(other, UUID):
            return self.root == other
        if isinstance(other, str):
            return self.root == UUID(other)
        return False
