
def print_transactions(processed_transactions):
    for transaction in processed_transactions:
        if transaction.is_valid:
            discount_str = f"{transaction.discount:.2f}" if transaction.discount > 0 else "-"

            print(f"{transaction.date} {transaction.package_size} {transaction.carrier} "
                  f"{transaction.final_price:.2f} {discount_str}")
        else:
            print(f"{transaction.raw_line} Ignored")
