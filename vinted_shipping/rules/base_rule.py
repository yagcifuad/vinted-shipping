from abc import ABC, abstractmethod

class BaseRule(ABC):
    """
    Abstract base class for discount rules.

    All discount rules should inherit from this class and implement
    the apply_rule method.
    """

    @abstractmethod
    def apply_rule(self, transaction, monthly_discount_tracker, l_lp_counter):
        """
        Apply this rule to a single transaction.

        Args:
            transaction (Transaction): A single transaction object.
            monthly_discount_tracker (dict): Tracker for monthly discounts.
            l_lp_counter (dict): Tracker for L LP shipments per month.

        Returns:
            dict: Updated monthly discount tracker
        """
        pass
