from datetime import datetime
from vinted_shipping.models.transaction import Transaction

def parse_input_file(file_path):
    transactions = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            transaction = Transaction('', '', '', line)

            if len(parts) == 3:
                try:
                    datetime.strptime(parts[0], '%Y-%m-%d')
                    date = parts[0]
                    package_size = parts[1]
                    carrier = parts[2]
                    transaction = Transaction(date, package_size, carrier, line)
                except ValueError:
                    transaction.is_valid = False
            else:
                transaction.is_valid = False

            transactions.append(transaction)

    return transactions
