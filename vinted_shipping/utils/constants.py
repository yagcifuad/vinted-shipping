"""
Constants for the Vinted shipping discount calculator.
"""

# Shipping price table by provider and package size
SHIPPING_PRICES = {
    'LP': {
        'S': 1.50,
        'M': 4.90,
        'L': 6.90
    },
    'MR': {
        'S': 2.00,
        'M': 3.00,
        'L': 4.00
    }
}

# Maximum monthly discount cap in euros
MONTHLY_DISCOUNT_CAP = 10.0