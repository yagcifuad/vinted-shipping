
from datetime import datetime


class Transaction:

    def __init__(self, date, package_size, carrier, raw_line):

        self.date = date
        self.package_size = package_size
        self.carrier = carrier
        self.raw_line = raw_line
        self.is_valid = self._validate()

        self.base_price = 0.0
        self.discount = 0.0
        self.final_price = 0.0

        if self.is_valid:
            self.date_obj = datetime.strptime(date, "%Y-%m-%d")
            self.year_month = f"{self.date_obj.year}-{self.date_obj.month:02d}"

    def _validate(self):

        valid_sizes = ['S', 'M', 'L']
        valid_carriers = ['LP', 'MR']

        return (self.package_size in valid_sizes and
                self.carrier in valid_carriers)

    def apply_discount(self, discount_amount):

        self.discount = min(discount_amount, self.base_price)
        self.final_price = self.base_price - self.discount

    def __repr__(self):
        return (f"Transaction({self.date}, {self.package_size}, {self.carrier}, "
                f"base_price={self.base_price:.2f}, discount={self.discount})")