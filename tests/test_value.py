from typing import Hashable
from unittest import TestCase
from uuid import UUID, uuid4

from pydantic import ValidationError

from pydddantic import Value


class ValueTests(TestCase):
    def test_value_should_be_immutable(self):
        # Given
        class Size(Value[int]): ...
        value = Size(1)

        # Expect
        with self.assertRaises(ValidationError) as exc:
            value.root = 2

        err = exc.exception.errors()[0]
        self.assertEqual("root", err["loc"][0])
        self.assertEqual("frozen_instance", err["type"])

    def test_should_equal_value_of_same_type_as_root(self):
        # Given
        class Size(Value[int]): ...

        # When
        value = Size(1)

        # Expect
        self.assertEqual(1, value)

    def test_should_not_equal_value_of_different_type_from_root(self):
        # Given
        class Size(Value[int]): ...

        # When
        value = Size(1)

        # Expect
        self.assertNotEqual("1", value)

    def test_same_root_values_should_be_equal(self):
        # Given
        class Size(Value[int]): ...

        # When
        value1 = Size(1)
        value2 = Size(1)

        # Expect
        self.assertEqual(value1, value2)

    def test_same_root_values_on_different_value_classes_should_be_equal(self):
        # Given
        class Width(Value[int]): ...
        class Height(Value[int]): ...

        # When
        value1 = Width(3)
        value2 = Height(3)

        # Expect
        self.assertEqual(value1, value2)

    def test_different_root_values_should_not_be_equal(self):
        # Given
        class Size(Value[int]): ...

        # When
        value1 = Size(1)
        value2 = Size(2)

        # Expect
        self.assertNotEqual(value1, value2)

    def test_value_string_should_be_root_string_value(self):
        # Given
        class MyId(Value[UUID]): ...
        id = uuid4()

        # When
        value = MyId(id)

        # Expect
        self.assertEqual(str(id), str(value))

    def test_value_should_be_hashable(self):
        # Given
        class MyValue(Value[int]): ...

        value = MyValue(1)

        # Expect
        self.assertIsInstance(value, Hashable)
