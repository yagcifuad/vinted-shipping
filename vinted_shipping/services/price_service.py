from vinted_shipping.utils.constants import SHIPPING_PRICES


def get_base_price(transaction):
    if not transaction.is_valid:
        return 0.0

    return SHIPPING_PRICES[transaction.carrier][transaction.package_size]


def get_lowest_s_price():
    return min(SHIPPING_PRICES[carrier]['S'] for carrier in SHIPPING_PRICES)