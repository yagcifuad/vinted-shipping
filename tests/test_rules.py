import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from vinted_shipping.models.transaction import Transaction
from vinted_shipping.utils.constants import SHIPPING_PRICES


class TestRules(unittest.TestCase):
    def setUp(self):
        self.lowest_s_rule = MagicMock()
        self.third_l_free_rule = MagicMock()

        def lowest_s_rule_apply(transaction, monthly_discount_tracker, l_lp_counter):
            if transaction.package_size != "S":
                return

            month = transaction.date[:7]

            if transaction.carrier == "MR" and transaction.package_size == "S":
                potential_discount = 0.50

                monthly_cap = 10.0
                remaining_discount = monthly_cap - monthly_discount_tracker.get(month, 0)
                applicable_discount = min(potential_discount, remaining_discount)

                if applicable_discount > 0:
                    transaction.discount = applicable_discount
                    transaction.final_price -= applicable_discount
                    monthly_discount_tracker[month] += applicable_discount

        def third_l_free_rule_apply(transaction, monthly_discount_tracker, l_lp_counter):
            if transaction.package_size != "L" or transaction.carrier != "LP":
                return

            month = transaction.date[:7]

            l_lp_counter[month] = l_lp_counter.get(month, 0) + 1

            if l_lp_counter[month] == 3:
                potential_discount = 6.90

                monthly_cap = 10.0
                remaining_discount = monthly_cap - monthly_discount_tracker.get(month, 0)
                applicable_discount = min(potential_discount, remaining_discount)

                if applicable_discount > 0:
                    transaction.discount = applicable_discount
                    transaction.final_price -= applicable_discount
                    monthly_discount_tracker[month] += applicable_discount

        self.lowest_s_rule.apply_rule.side_effect = lowest_s_rule_apply
        self.third_l_free_rule.apply_rule.side_effect = third_l_free_rule_apply

        self.monthly_discount_tracker = {"2015-02": 0.0, "2015-03": 0.0}
        self.l_lp_counter = {"2015-02": 0, "2015-03": 0}

    def create_transaction(self, date, package_size, carrier):
        transaction = Transaction(date, package_size, carrier, f"{date} {package_size} {carrier}")
        transaction.base_price = SHIPPING_PRICES[carrier][package_size]
        transaction.final_price = transaction.base_price
        transaction.discount = 0.0
        return transaction

    def test_lowest_s_rule_applies_discount(self):
        transaction = self.create_transaction("2015-02-01", "S", "MR")

        self.lowest_s_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(transaction.discount, 0.50)
        self.assertEqual(transaction.final_price, 1.50)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 0.50)

    def test_lowest_s_rule_no_discount_needed(self):
        transaction = self.create_transaction("2015-02-01", "S", "LP")

        self.lowest_s_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(transaction.discount, 0.0)
        self.assertEqual(transaction.final_price, 1.50)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 0.0)

    def test_lowest_s_rule_respects_monthly_cap(self):
        self.monthly_discount_tracker["2015-02"] = 9.80

        transaction = self.create_transaction("2015-02-01", "S", "MR")

        self.lowest_s_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertAlmostEqual(transaction.discount, 0.20, places=10)
        self.assertAlmostEqual(transaction.final_price, 1.80, places=10)
        self.assertAlmostEqual(self.monthly_discount_tracker["2015-02"], 10.0, places=10)

    def test_lowest_s_rule_ignores_non_s_packages(self):
        transaction = self.create_transaction("2015-02-01", "M", "MR")

        self.lowest_s_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(transaction.discount, 0.0)
        self.assertEqual(transaction.final_price, 3.0)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 0.0)

    def test_third_l_free_rule_increments_counter(self):
        transaction = self.create_transaction("2015-02-01", "L", "LP")

        self.third_l_free_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 1)
        self.assertEqual(transaction.discount, 0.0)

    def test_third_l_free_rule_applies_discount_on_third(self):
        self.l_lp_counter["2015-02"] = 2

        transaction = self.create_transaction("2015-02-01", "L", "LP")

        self.third_l_free_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 3)
        self.assertEqual(transaction.discount, 6.90)
        self.assertEqual(transaction.final_price, 0.0)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 6.90)

    def test_third_l_free_rule_respects_monthly_cap(self):
        self.l_lp_counter["2015-02"] = 2
        self.monthly_discount_tracker["2015-02"] = 8.0

        transaction = self.create_transaction("2015-02-01", "L", "LP")

        self.third_l_free_rule.apply_rule(transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 3)
        self.assertEqual(transaction.discount, 2.0)
        self.assertEqual(transaction.final_price, 4.90)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 10.0)

    def test_third_l_free_rule_ignores_non_l_lp_packages(self):
        transaction1 = self.create_transaction("2015-02-01", "L", "MR")

        self.third_l_free_rule.apply_rule(transaction1, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 0)
        self.assertEqual(transaction1.discount, 0.0)

        transaction2 = self.create_transaction("2015-02-01", "M", "LP")

        self.third_l_free_rule.apply_rule(transaction2, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 0)
        self.assertEqual(transaction2.discount, 0.0)

    def test_multiple_rules_interaction(self):
        s_transaction = self.create_transaction("2015-02-01", "S", "MR")
        self.lowest_s_rule.apply_rule(s_transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(s_transaction.discount, 0.50)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 0.50)

        l_transaction1 = self.create_transaction("2015-02-02", "L", "LP")
        l_transaction2 = self.create_transaction("2015-02-03", "L", "LP")

        self.third_l_free_rule.apply_rule(l_transaction1, self.monthly_discount_tracker, self.l_lp_counter)
        self.third_l_free_rule.apply_rule(l_transaction2, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 2)
        self.assertEqual(l_transaction1.discount, 0.0)
        self.assertEqual(l_transaction2.discount, 0.0)

        l_transaction3 = self.create_transaction("2015-02-04", "L", "LP")
        self.third_l_free_rule.apply_rule(l_transaction3, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 3)
        self.assertEqual(l_transaction3.discount, 6.90)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 7.40)

        s_transaction2 = self.create_transaction("2015-02-05", "S", "MR")
        self.lowest_s_rule.apply_rule(s_transaction2, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(s_transaction2.discount, 0.50)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 7.90)

    def test_monthly_cap_enforcement(self):
        self.monthly_discount_tracker["2015-02"] = 9.80

        s_transaction = self.create_transaction("2015-02-01", "S", "MR")
        self.lowest_s_rule.apply_rule(s_transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertAlmostEqual(s_transaction.discount, 0.20, places=10)
        self.assertAlmostEqual(self.monthly_discount_tracker["2015-02"], 10.0, places=10)

        self.l_lp_counter["2015-02"] = 2

        l_transaction = self.create_transaction("2015-02-04", "L", "LP")
        self.third_l_free_rule.apply_rule(l_transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(self.l_lp_counter["2015-02"], 3)
        self.assertEqual(l_transaction.discount, 0.0)
        self.assertAlmostEqual(self.monthly_discount_tracker["2015-02"], 10.0, places=10)

    def test_different_months_tracking(self):
        feb_transaction = self.create_transaction("2015-02-01", "S", "MR")
        self.lowest_s_rule.apply_rule(feb_transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(feb_transaction.discount, 0.50)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 0.50)

        mar_transaction = self.create_transaction("2015-03-01", "S", "MR")
        self.lowest_s_rule.apply_rule(mar_transaction, self.monthly_discount_tracker, self.l_lp_counter)

        self.assertEqual(mar_transaction.discount, 0.50)
        self.assertEqual(self.monthly_discount_tracker["2015-03"], 0.50)
        self.assertEqual(self.monthly_discount_tracker["2015-02"], 0.50)


if __name__ == '__main__':
    unittest.main()