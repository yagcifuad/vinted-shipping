"""
Initialize rules module and provide rule registry.
"""
from vinted_shipping.rules.lowest_s_rule import LowestSRule
from vinted_shipping.rules.third_l_free_rule import ThirdLFreeRule

# Register all rules in the order they should be applied
RULES = [
    LowestSRule(),
    ThirdLFreeRule()
]