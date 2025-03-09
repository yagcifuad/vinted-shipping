from collections import defaultdict
from vinted_shipping.services.price_service import get_base_price
from vinted_shipping.rules import RULES


def calculate_discounts(transactions):

    monthly_discount_tracker = defaultdict(float)

    l_lp_counter = defaultdict(int)

    for transaction in transactions:
        if transaction.is_valid:

            transaction.base_price = get_base_price(transaction)
            transaction.final_price = transaction.base_price

            year_month = transaction.year_month
            if monthly_discount_tracker[year_month] >= 10.0:
                continue

            for rule in RULES:
                rule.apply_rule(transaction, monthly_discount_tracker, l_lp_counter)

    return transactions
