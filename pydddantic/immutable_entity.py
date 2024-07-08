from abc import ABC

from pydantic import ConfigDict

from .entity import Entity


class ImmutableEntity(Entity, ABC):
    """
    Abstract base class for an immutable Domain Entity that should not be modified after creation.
    """

    model_config = ConfigDict(frozen=True)
