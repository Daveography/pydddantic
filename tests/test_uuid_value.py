from unittest import TestCase
from uuid import UUID

from pydddantic import UUIDValue


class UUIDValueTests(TestCase):
    def test_should_generate_a_new_uuid(self):
        # Given
        class UserId(UUIDValue): ...

        # When
        user_id = UserId.generate()

        # Expect
        self.assertIsInstance(user_id, UserId)
        self.assertIsInstance(user_id.root, UUID)

    def test_should_create_uuid_from_string(self):
        # Given
        class UserId(UUIDValue): ...

        # When
        user_id = UserId("db5b3fe1-3631-4ac4-8b91-b8333da02616")

        # Expect
        self.assertIsInstance(user_id, UserId)
        self.assertIsInstance(user_id.root, UUID)

    def test_same_ids_should_be_equivalent(self):
        # Given
        class UserId(UUIDValue): ...

        id = "db5b3fe1-3631-4ac4-8b91-b8333da02616"

        # When
        user_id1 = UserId(id)
        user_id2 = UserId(id)

        # Expect
        self.assertEqual(user_id1, user_id2)

    def test_id_should_be_equivalent_to_string(self):
        # Given
        class UserId(UUIDValue): ...

        id = "db5b3fe1-3631-4ac4-8b91-b8333da02616"

        # When
        user_id = UserId(id)

        # Expect
        self.assertEqual(id, user_id)

    def test_id_should_not_be_equivalent_to_unsupported_comparison_type(self):
        # Given
        class UserId(UUIDValue): ...
        class UnknownType: ...

        # When
        user_id = UserId("db5b3fe1-3631-4ac4-8b91-b8333da02616")
        other = UnknownType()

        # Expect
        self.assertNotEqual(user_id, other)
