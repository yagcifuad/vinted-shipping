from vinted_shipping.rules.base_rule import BaseRule
from vinted_shipping.services.price_service import get_lowest_s_price
from vinted_shipping.utils.constants import MONTHLY_DISCOUNT_CAP

class LowestSRule(BaseRule):

    def apply_rule(self, transaction, monthly_discount_tracker, l_lp_counter):

        if transaction.package_size == 'S':
            year_month = transaction.year_month

            if monthly_discount_tracker[year_month] >= MONTHLY_DISCOUNT_CAP:
                return

            lowest_s_price = get_lowest_s_price()
            if transaction.base_price > lowest_s_price:
                discount_amount = transaction.base_price - lowest_s_price

                remaining_budget = max(0, MONTHLY_DISCOUNT_CAP - monthly_discount_tracker[year_month])
                applicable_discount = min(discount_amount, remaining_budget)

                transaction.apply_discount(applicable_discount)

                monthly_discount_tracker[year_month] += applicable_discount
