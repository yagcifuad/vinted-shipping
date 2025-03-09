import sys
from vinted_shipping.services.parser_service import parse_input_file
from vinted_shipping.services.discount_service import calculate_discounts
from vinted_shipping.services.print_service import print_transactions


def main():

    input_file = sys.argv[1] if len(sys.argv) > 1 else '../input.txt'

    try:
        transactions = parse_input_file(input_file)

        processed_transactions = calculate_discounts(transactions)

        print_transactions(processed_transactions)

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()