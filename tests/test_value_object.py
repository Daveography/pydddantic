from typing import Hashable
from unittest import TestCase

from pydantic import ValidationError

from pydddantic import ValueObject


class ValueObjectTests(TestCase):
    def test_value_object_should_be_immutable(self):
        # Given
        class DeliveryBox(ValueObject):
            size: int

        value = DeliveryBox(size=1)

        # Expect
        with self.assertRaises(ValidationError) as exc:
            value.size = 2

        err = exc.exception.errors()[0]
        self.assertEqual("size", err["loc"][0])
        self.assertEqual("frozen_instance", err["type"])

    def test_identical_value_objects_should_be_equal(self):
        # Given
        class DeliveryBox(ValueObject):
            type: str
            size: int

        # When
        value1 = DeliveryBox(type="tiny", size=1)
        value2 = DeliveryBox(type="tiny", size=1)

        # Expect
        self.assertEqual(value1, value2)

    def test_different_value_objects_should_not_be_equal(self):
        # Given
        class DeliveryBox(ValueObject):
            type: str
            size: int

        # When
        value1 = DeliveryBox(type="tiny", size=1)
        value2 = DeliveryBox(type="small", size=2)

        # Expect
        self.assertNotEqual(value1, value2)

    def test_different_value_object_classes_with_same_values_should_not_be_equal(self):
        # Given
        class DeliveryBox(ValueObject):
            type: str
            size: int

        class Envelope(ValueObject):
            type: str
            size: int

        # When
        value1 = DeliveryBox(type="tiny", size=1)
        value2 = Envelope(type="tiny", size=1)

        # Expect
        self.assertNotEqual(value1, value2)

    def test_value_object_should_be_hashable(self):
        # Given
        class DeliveryBox(ValueObject):
            size: int

        value = DeliveryBox(size=1)

        # Expect
        self.assertIsInstance(value, Hashable)
