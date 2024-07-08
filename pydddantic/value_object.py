from abc import ABC

from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel, ABC):
    """
    Abstract base class for an immutable Value Object using Pydantic's BaseModel.
    """

    model_config = ConfigDict(frozen=True)
