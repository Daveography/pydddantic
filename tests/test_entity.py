from typing_extensions import Annotated, Hashable
from unittest import TestCase
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from pydddantic import Entity


class EntityTests(TestCase):
    def test_entity_id_should_be_immutable(self):
        # Given
        class User(Entity):
            name: str

        user = User(id=uuid4(), name="Alice")

        # Expect
        with self.assertRaises(ValidationError) as exc:
            user.id = uuid4()

        err = exc.exception.errors()[0]
        self.assertEqual("id", err["loc"][0])
        self.assertEqual("frozen_field", err["type"])

    def test_overridden_id_field_annotation_should_be_immutable_when_annotated(self):
        # Given
        class User(Entity):
            id: Annotated[UUID, Entity.IdField]
            name: str

        user = User(id=uuid4(), name="Alice")

        # Expect
        with self.assertRaises(ValidationError) as exc:
            user.id = uuid4()

        err = exc.exception.errors()[0]
        self.assertEqual("id", err["loc"][0])
        self.assertEqual("frozen_field", err["type"])

    def test_entity_fields_should_be_mutable(self):
        # Given
        class User(Entity):
            name: str

        user = User(id=uuid4(), name="Alice")

        # When
        user.name = "Bob"

        # Expect
        self.assertEqual("Bob", user.name)

    def test_entity_fields_should_revalidate_on_assignment(self):
        # Given
        class User(Entity):
            name: str = Field(max_length=30)

        user = User(id=uuid4(), name="Alice")

        # Expect
        with self.assertRaises(ValidationError) as exc:
            user.name = "John Jacob Jingleheimer Schmidt"

        err = exc.exception.errors()[0]
        self.assertEqual("name", err["loc"][0])
        self.assertEqual("string_too_long", err["type"])

    def test_entities_with_same_id_should_be_equal(self):
        # Given
        class User(Entity):
            name: str

        id = uuid4()

        # When
        alice = User(id=id, name="Alice")
        bob = User(id=id, name="Bob")

        # Expect
        self.assertEqual(alice, bob)

    def test_entities_with_different_id_should_not_be_equal(self):
        # Given
        class User(Entity):
            name: str

        # When
        alice1 = User(id=uuid4(), name="Alice")
        alice2 = User(id=uuid4(), name="Alice")

        # Expect
        self.assertNotEqual(alice1, alice2)

    def test_different_entity_classes_with_same_values_should_not_be_equal(self):
        # Given
        class User(Entity):
            name: str

        class Customer(Entity):
            name: str

        id = uuid4()

        # When
        alice1 = User(id=id, name="Alice")
        alice2 = Customer(id=id, name="Alice")

        # Expect
        self.assertNotEqual(alice1, alice2)

    def test_entity_should_be_hashable(self):
        # Given
        class User(Entity):
            name: str

        value = User(id=uuid4(), name="Alice")

        # Expect
        self.assertIsInstance(value, Hashable)

    def test_entities_with_same_id_should_have_same_hash(self):
        # Given
        class User(Entity):
            name: str

        id = uuid4()

        # When
        alice = User(id=id, name="Alice")
        bob = User(id=id, name="Bob")

        # Expect
        self.assertEqual(hash(alice), hash(bob))
