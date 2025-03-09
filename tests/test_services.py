import unittest
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from collections import defaultdict

from vinted_shipping.models.transaction import Transaction
from vinted_shipping.services.parser_service import parse_input_file
from vinted_shipping.services.discount_service import calculate_discounts
from vinted_shipping.services.price_service import get_base_price, get_lowest_s_price
from vinted_shipping.services.print_service import print_transactions
from vinted_shipping.utils.constants import SHIPPING_PRICES


class TestParserService(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="2015-02-01 S MR\n2015-02-02 M LP\n2015-02-03 INVALID\n")
    def test_parse_input_file(self, mock_file):
        transactions = parse_input_file("dummy/path")

        self.assertEqual(len(transactions), 3)

        self.assertTrue(transactions[0].is_valid)
        self.assertEqual(transactions[0].date, "2015-02-01")
        self.assertEqual(transactions[0].package_size, "S")
        self.assertEqual(transactions[0].carrier, "MR")

        self.assertTrue(transactions[1].is_valid)
        self.assertEqual(transactions[1].date, "2015-02-02")
        self.assertEqual(transactions[1].package_size, "M")
        self.assertEqual(transactions[1].carrier, "LP")

        self.assertFalse(transactions[2].is_valid)

    @patch("builtins.open", new_callable=mock_open, read_data="invalid_date S MR\n")
    def test_parse_invalid_date(self, mock_file):
        transactions = parse_input_file("dummy/path")

        self.assertEqual(len(transactions), 1)
        self.assertFalse(transactions[0].is_valid)


class TestPriceService(unittest.TestCase):

    def test_get_base_price_valid_transaction(self):
        for carrier in SHIPPING_PRICES:
            for size in SHIPPING_PRICES[carrier]:
                transaction = Transaction("2015-02-01", size, carrier, "2015-02-01 {size} {carrier}")
                expected_price = SHIPPING_PRICES[carrier][size]

                self.assertEqual(get_base_price(transaction), expected_price)

    def test_get_base_price_invalid_transaction(self):
        transaction = Transaction("2015-02-01", "XL", "DHL", "2015-02-01 XL DHL")
        transaction.is_valid = False

        self.assertEqual(get_base_price(transaction), 0.0)

    def test_get_lowest_s_price(self):
        lowest_s = min(SHIPPING_PRICES[carrier]['S'] for carrier in SHIPPING_PRICES)

        self.assertEqual(get_lowest_s_price(), lowest_s)
        self.assertEqual(get_lowest_s_price(), 1.50)


class TestDiscountService(unittest.TestCase):

    def setUp(self):
        self.transactions = [
            Transaction("2015-02-01", "S", "MR", "2015-02-01 S MR"),
            Transaction("2015-02-02", "S", "LP", "2015-02-02 S LP"),
            Transaction("2015-02-03", "L", "LP", "2015-02-03 L LP"),
            Transaction("2015-02-04", "L", "LP", "2015-02-04 L LP"),
            Transaction("2015-02-05", "L", "LP", "2015-02-05 L LP"),
            Transaction("2015-02-06", "L", "MR", "2015-02-06 L MR"),
            Transaction("2015-02-07", "M", "MR", "2015-02-07 M MR"),

            Transaction("2015-02-08", "XL", "DHL", "2015-02-08 XL DHL")
        ]

        for transaction in self.transactions:
            if transaction.is_valid:
                transaction.base_price = get_base_price(transaction)

    def test_calculate_discounts(self):
        processed = calculate_discounts(self.transactions)

        self.assertEqual(processed[0].discount, 0.5)
        self.assertEqual(processed[0].final_price, 1.5)

        self.assertEqual(processed[1].discount, 0.0)
        self.assertEqual(processed[1].final_price, 1.5)

        self.assertEqual(processed[2].discount, 0.0)
        self.assertEqual(processed[2].final_price, 6.9)
        self.assertEqual(processed[3].discount, 0.0)
        self.assertEqual(processed[3].final_price, 6.9)

        self.assertEqual(processed[4].discount, 6.9)
        self.assertEqual(processed[4].final_price, 0.0)

        self.assertEqual(processed[5].discount, 0.0)
        self.assertEqual(processed[5].final_price, 4.0)

        self.assertEqual(processed[6].discount, 0.0)
        self.assertEqual(processed[6].final_price, 3.0)

        self.assertEqual(processed[7].base_price, 0.0)
        self.assertEqual(processed[7].discount, 0.0)

    def test_monthly_discount_cap(self):
        many_s_transactions = []
        for i in range(30):
            transaction = Transaction("2015-02-01", "S", "MR", f"2015-02-01 S MR #{i}")
            transaction.base_price = 2.0
            many_s_transactions.append(transaction)

        processed = calculate_discounts(many_s_transactions)

        total_discount = sum(t.discount for t in processed)

        self.assertLessEqual(total_discount, 10.0)

        for i in range(20):
            self.assertEqual(processed[i].discount, 0.5)
            self.assertEqual(processed[i].final_price, 1.5)

        for i in range(20, 30):
            self.assertEqual(processed[i].discount, 0.0)
            self.assertEqual(processed[i].final_price, 2.0)


class TestPrintService(unittest.TestCase):

    @patch("builtins.print")
    def test_print_valid_transactions(self, mock_print):
        t1 = Transaction("2015-02-01", "S", "MR", "2015-02-01 S MR")
        t1.base_price = 2.0
        t1.discount = 0.5
        t1.final_price = 1.5

        t2 = Transaction("2015-02-02", "M", "LP", "2015-02-02 M LP")
        t2.base_price = 4.9
        t2.discount = 0.0
        t2.final_price = 4.9

        print_transactions([t1, t2])

        mock_print.assert_any_call("2015-02-01 S MR 1.50 0.50")
        mock_print.assert_any_call("2015-02-02 M LP 4.90 -")

    @patch("builtins.print")
    def test_print_invalid_transactions(self, mock_print):
        t = Transaction("2015-02-29", "CUSPS", "INVALID", "2015-02-29 CUSPS")
        t.is_valid = False

        print_transactions([t])

        mock_print.assert_called_once_with("2015-02-29 CUSPS Ignored")


if __name__ == '__main__':
    unittest.main()