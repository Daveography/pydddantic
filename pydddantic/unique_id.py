from abc import ABC
from typing_extensions import Self
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class UniqueId(UUID, ABC):
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
        # TODO: Not sure this is the correct way to do this, but it works for now.
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(UUID),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            # Accept the UUID as already validated by its own type
                            core_schema.no_info_plain_validator_function(lambda x: x),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )

    def __eq__(self, other: str | UUID) -> bool:
        if isinstance(other, str):
            return self == UUID(other)
        if isinstance(other, UniqueId) and not isinstance(other, type(self)):
            return False
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.int)
