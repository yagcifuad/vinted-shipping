import unittest
from datetime import datetime
from vinted_shipping.models.transaction import Transaction


class TestTransaction(unittest.TestCase):
    def test_valid_transaction_initialization(self):
        transaction = Transaction("2015-02-01", "S", "MR", "2015-02-01 S MR")

        self.assertTrue(transaction.is_valid)
        self.assertEqual(transaction.date, "2015-02-01")
        self.assertEqual(transaction.package_size, "S")
        self.assertEqual(transaction.carrier, "MR")
        self.assertEqual(transaction.raw_line, "2015-02-01 S MR")
        self.assertEqual(transaction.year_month, "2015-02")
        self.assertEqual(transaction.base_price, 0.0)
        self.assertEqual(transaction.discount, 0.0)
        self.assertEqual(transaction.final_price, 0.0)

    def test_invalid_package_size(self):
        transaction = Transaction("2015-02-01", "XL", "MR", "2015-02-01 XL MR")

        self.assertFalse(transaction.is_valid)

    def test_invalid_carrier(self):
        transaction = Transaction("2015-02-01", "S", "DHL", "2015-02-01 S DHL")

        self.assertFalse(transaction.is_valid)

    def test_date_object_creation(self):
        transaction = Transaction("2015-02-01", "S", "MR", "2015-02-01 S MR")

        self.assertEqual(transaction.date_obj, datetime(2015, 2, 1))

    def test_apply_discount(self):
        transaction = Transaction("2015-02-01", "S", "MR", "2015-02-01 S MR")
        transaction.base_price = 2.0

        transaction.apply_discount(0.5)
        self.assertEqual(transaction.discount, 0.5)
        self.assertEqual(transaction.final_price, 1.5)

        transaction.apply_discount(3.0)
        self.assertEqual(transaction.discount, 2.0)
        self.assertEqual(transaction.final_price, 0.0)

    def test_repr(self):
        transaction = Transaction("2015-02-01", "S", "MR", "2015-02-01 S MR")
        transaction.base_price = 2.0
        transaction.discount = 0.5

        expected_repr = "Transaction(2015-02-01, S, MR, base_price=2.00, discount=0.5)"
        self.assertEqual(repr(transaction), expected_repr)


if __name__ == '__main__':
    unittest.main()