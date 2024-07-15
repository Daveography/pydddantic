from unittest import TestCase
from uuid import UUID

from pydantic import UUID4, BaseModel

from pydddantic import UUIDValue


class UUIDValueTests(TestCase):
    def test_should_generate_a_new_id(self):
        # Given
        class UserId(UUIDValue): ...

        # When
        user_id = UserId.generate()

        # Expect
        self.assertIsInstance(user_id, UserId)
        self.assertIsInstance(user_id, UUID)

    def test_should_create_id_from_string(self):
        # Given
        class UserId(UUIDValue): ...
        id_str = "db5b3fe1-3631-4ac4-8b91-b8333da02616"

        # When
        user_id = UserId(id_str)

        # Expect
        self.assertEqual(id_str, user_id)

    def test_should_create_id_from_uuid(self):
        # Given
        class UserId(UUIDValue): ...
        uuid = UUID("db5b3fe1-3631-4ac4-8b91-b8333da02616")

        # When
        user_id = UserId(uuid)

        # Expect
        self.assertEqual(uuid, user_id)

    def test_same_ids_should_be_equivalent(self):
        # Given
        class UserId(UUIDValue): ...

        id = "db5b3fe1-3631-4ac4-8b91-b8333da02616"

        # When
        user_id1 = UserId(id)
        user_id2 = UserId(id)

        # Expect
        self.assertEqual(user_id1, user_id2)

    def test_different_ids_should_not_be_equivalent(self):
        # Given
        class UserId(UUIDValue): ...

        id1 = "db5b3fe1-3631-4ac4-8b91-b8333da02616"
        id2 = "a40e6a48-2136-485b-9961-3269e6f83a97"

        # When
        user_id1 = UserId(id1)
        user_id2 = UserId(id2)

        # Expect
        self.assertNotEqual(user_id1, user_id2)

    def test_same_ids_of_different_classes_should_not_be_equivalent(self):
        # Given
        class UserId(UUIDValue): ...
        class AccountId(UUIDValue): ...

        id = "db5b3fe1-3631-4ac4-8b91-b8333da02616"

        # When
        user_id = UserId(id)
        account_id = AccountId(id)

        # Expect
        self.assertNotEqual(user_id, account_id)

    def test_different_classes_should_be_different_instances(self):
        # Given
        class UserId(UUIDValue): ...
        class AccountId(UUIDValue): ...

        # When
        user_id = UserId("db5b3fe1-3631-4ac4-8b91-b8333da02616")
        account_id = AccountId("a9cb74b9-540d-4a50-9631-563b6b13c37c")

        # Expect
        self.assertNotIsInstance(user_id, AccountId)
        self.assertNotIsInstance(account_id, UserId)

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

    def test_id_value_should_be_compatible_with_uuid4(self):
        # Given
        class UserId(UUIDValue): ...

        class User(BaseModel):
            id: UUID4

        user_id = UserId("db5b3fe1-3631-4ac4-8b91-b8333da02616")

        # When
        user = User(id=user_id)

        # Expect
        self.assertEqual(user_id, user.id)
