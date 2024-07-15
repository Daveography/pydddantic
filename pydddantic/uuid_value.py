from abc import ABC
from typing_extensions import Self
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class UUIDValue(UUID, ABC):
    def __init__(self, uuid: str | UUID):
        if isinstance(uuid, UUID):
            super().__init__(bytes=uuid.bytes)
        else:
            super().__init__(uuid)

    @classmethod
    def generate(cls) -> Self:
        return cls(uuid4())

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type[object], handler: GetCoreSchemaHandler) -> CoreSchema:
        if issubclass(source_type, UUID):
            # Accept the UUID as already validated by its own type
            # TODO: Not sure this is the correct way to do this, but it works for now.
            return core_schema.no_info_plain_validator_function(lambda x: x)
        return core_schema.no_info_plain_validator_function(UUID)

    def __eq__(self, other: str | UUID) -> bool:
        if isinstance(other, str):
            return self == UUID(other)
        if isinstance(other, UUIDValue) and not isinstance(other, type(self)):
            return False
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.int)
