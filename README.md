# Vinted Shipping Calculator

This repository is the solution for the **Vinted Backend Homework Assignment**. The project calculates shipping discounts for Vinted transactions by applying a set of customizable rules. In keeping with Vinted’s philosophy, the code is clean, simple, well-tested, and maintainable.

## Project Overview

- **Domain:** Shipping discount calculation based on transaction rules.
- **Features:**
  - Parses transaction data from an input file.
  - Determines base shipping prices based on package size and carrier.
  - Applies discount rules:
    - **S Package Rule:** Always charges the lowest S package price among available providers.
    - **LP L Shipment Rule:** Makes the third LP shipment for L packages free, once per calendar month.
    - **Monthly Discount Cap:** Ensures that accumulated discounts do not exceed €10 per month.
  - Outputs transaction details along with discounts applied (or a '-' if no discount is provided).

## Project Structure

- **input.txt** – File containing transaction data (one transaction per line).
- **vinted_shipping/** – Main package directory containing:
  - **main.py** – Application entry-point.
  - **models/** – Contains the `Transaction` model.
  - **rules/** – Discount rules are implemented here (`LowestSRule`, `ThirdLFreeRule`)
  - **services/** – Provides functionality to parse input, calculate discounts, and print transactions.
  - **utils/** – Contains constants and shared utilities.
- **tests/** – Unit tests for the application.

## Getting Started

### Prerequisites

- Python 3.6 or higher.

### Running the Application

- **Direct Execution (using default input file):**

```bash
    python3 -m vinted_shipping.main
```

- **With Specified Input File:**

```bash
    python3 -m vinted_shipping.main /path/to/input.txt
```

### Running Tests

Execute the tests with:

```bash
    pytest
```


## Design Decisions & Assumptions

- **Modular Rules:** Each discount rule is implemented as a separate module, ensuring that new rules can be added or modified easily.
- **Input & Validation:** The solution loads data from a file (default: `input.txt`). Lines that are improperly formatted or reference unknown carriers/package sizes are marked as invalid and output with "Ignored".
- **Discount Mechanism:**
  - For **S** shipments, the rule calculates the discount so that the price matches the lowest available S price.
  - For **L** shipments via **LP**, once the third shipment in a calendar month is reached, the discount is applied to make the shipment free, subject to the remaining monthly discount budget.
  - The monthly discount is capped at €10, with any remaining funds applied as a partial discount if necessary.

## Repository

Clone the repository using the following command:

```bash
git clone https://github.com/yagcifuad/vinted-shipping
```

## License

This project is licensed under the MIT License.
