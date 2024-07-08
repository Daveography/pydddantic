from unittest import TestCase
from uuid import uuid4

from pydantic import ValidationError

from pydddantic import ImmutableEntity


class ImmutableEntityTests(TestCase):
    def test_entity_fields_should_be_immutable(self):
        # Given
        class ReadOnlyUser(ImmutableEntity):
            name: str

        user = ReadOnlyUser(id=uuid4(), name="Alice")

        # Expect
        with self.assertRaises(ValidationError) as exc:
            user.name = "Bob"

        err = exc.exception.errors()[0]
        self.assertEqual("name", err["loc"][0])
        self.assertEqual("frozen_instance", err["type"])
