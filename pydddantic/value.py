from __future__ import annotations

from abc import ABC
from typing_extensions import TypeVar

from pydantic import ConfigDict, RootModel

T = TypeVar("T")


class Value(RootModel[T], ABC):
    """
    Abstract base class for a simple immutable Value Type using Pydantic's RootModel (including any Pydantic
    validators).
    """

    model_config = ConfigDict(frozen=True)

    def __str__(self) -> str:
        return str(self.root)

    def __eq__(self, other: T | Value[T]) -> bool:
        if isinstance(other, Value):
            return self.root == other.root
        return self.root == other
