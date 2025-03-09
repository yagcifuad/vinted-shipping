from vinted_shipping.rules.base_rule import BaseRule
from vinted_shipping.utils.constants import MONTHLY_DISCOUNT_CAP

class ThirdLFreeRule(BaseRule):

    def apply_rule(self, transaction, monthly_discount_tracker, l_lp_counter):

        if transaction.package_size == 'L' and transaction.carrier == 'LP':
            year_month = transaction.year_month
            l_lp_counter[year_month] += 1

            if l_lp_counter[year_month] == 3:

                if monthly_discount_tracker[year_month] >= MONTHLY_DISCOUNT_CAP:
                    return

                remaining_budget = max(0, MONTHLY_DISCOUNT_CAP - monthly_discount_tracker[year_month])
                applicable_discount = min(transaction.base_price, remaining_budget)

                transaction.apply_discount(applicable_discount)

                monthly_discount_tracker[year_month] += applicable_discount
