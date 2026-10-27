
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
import csv

# ----------------------------------------
# 1. CONFIGURATION
# ----------------------------------------

# Base fare for each public transport route (in INR)
ROUTES = {
    "R101": {"name": "City Center - Railway Station", "base_fare": Decimal("30.00")},
    "R102": {"name": "City Center - Airport", "base_fare": Decimal("80.00")},
    "R103": {"name": "Railway Station - University", "base_fare": Decimal("25.00")},
    "R104": {"name": "University - Airport", "base_fare": Decimal("60.00")},
}

# Discounts by passenger category
PASSENGER_CATEGORIES = {
    "adult": Decimal("0.00"),
    "student": Decimal("0.30"),
    "senior": Decimal("0.40"),
    "child": Decimal("0.50"),
    "disabled": Decimal("0.50"),
}

# Allowed difference before flagging a discrepancy
TOLERANCE = Decimal("0.01")


def money(amount):
    """Round an amount to two decimal places."""
    return Decimal(str(amount)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


# ----------------------------------------
# 2. FARE CALCULATION
# ----------------------------------------

def calculate_fare(route_id, category, passengers=1):
    """Calculate the expected fare for a passenger group."""

    if route_id not in ROUTES:
        raise ValueError(f"Unknown route: {route_id}")

    if category not in PASSENGER_CATEGORIES:
        raise ValueError(f"Unknown passenger category: {category}")

    if not isinstance(passengers, int) or isinstance(passengers, bool) or passengers <= 0:
        raise ValueError("Passenger count must be a positive integer.")

    base_fare = ROUTES[route_id]["base_fare"]
    discount = PASSENGER_CATEGORIES[category]

    fare_per_passenger = money(base_fare * (1 - discount))
    total_fare = money(fare_per_passenger * passengers)

    return total_fare


# ----------------------------------------
# 3. REVENUE RECONCILIATION
# ----------------------------------------

def reconcile_transactions(transactions):
    """
    Each transaction contains:
    transaction_id, route_id, category, passengers,
    collected_amount.

    collected_amount=None indicates missing collection data.
    """

    results = []
    route_summary = defaultdict(
        lambda: {
            "expected": Decimal("0.00"),
            "collected": Decimal("0.00"),
            "transactions": 0,
            "missing": 0,
        }
    )

    category_summary = defaultdict(
        lambda: {
            "expected": Decimal("0.00"),
            "collected": Decimal("0.00"),
            "transactions": 0,
        }
    )

    for tx in transactions:
        transaction_id = tx.get("transaction_id", "UNKNOWN")
        route_id = tx.get("route_id")
        category = tx.get("category")
        passengers = tx.get("passengers", 1)
        collected = tx.get("collected_amount")

        # Validate the transaction before processing it.
        try:
            expected = calculate_fare(route_id, category, passengers)

            if collected is None or str(collected).strip() == "":
                collected_amount = None
            else:
                collected_amount = money(collected)
                if collected_amount < 0:
                    raise ValueError("Collected amount cannot be negative.")

        except (ValueError, TypeError, ArithmeticError) as exc:
            results.append({
                "transaction_id": transaction_id,
                "route_id": route_id,
                "category": category,
                "passengers": passengers,
                "expected": "",
                "collected": "" if collected is None else collected,
                "difference": "",
                "status": f"INVALID: {exc}",
            })
            continue

        if collected_amount is None:
            difference = None
            status = "MISSING COLLECTION DATA"
            route_summary[route_id]["missing"] += 1
        else:
            difference = money(collected_amount - expected)

            if difference < -TOLERANCE:
                status = "UNDER-COLLECTED"
            elif difference > TOLERANCE:
                status = "OVER-COLLECTED"
            else:
                status = "RECONCILED"

        results.append({
            "transaction_id": transaction_id,
            "route_id": route_id,
            "category": category,
            "passengers": passengers,
            "expected": str(expected),
            "collected": (
                "" if collected_amount is None
                else str(collected_amount)
            ),
            "difference": (
                "" if difference is None
                else str(difference)
            ),
            "status": status,
        })

        # Missing collection records are not counted as zero revenue.
        # They are reported separately to avoid misleading totals.
        summary = route_summary[route_id]
        summary["transactions"] += 1
        if collected_amount is not None:
            summary["expected"] += expected
            summary["collected"] += collected_amount

        cat_summary = category_summary[category]
        cat_summary["transactions"] += 1
        if collected_amount is not None:
            cat_summary["expected"] += expected
            cat_summary["collected"] += collected_amount

    return results, route_summary, category_summary


# ----------------------------------------
# 4. DISPLAY REPORTS
# ----------------------------------------

def print_transaction_report(results):
    print("\nTRANSACTION RECONCILIATION REPORT")
    print("-" * 105)
    print(
        f"{'ID':<10} {'Route':<8} {'Category':<10} "
        f"{'Expected':>12} {'Collected':>12} "
        f"{'Difference':>12}  Status"
    )
    print("-" * 105)

    for row in results:
        print(
            f"{row['transaction_id']:<10} "
            f"{str(row['route_id']):<8} "
            f"{str(row['category']):<10} "
            f"{str(row['expected']):>12} "
            f"{str(row['collected']):>12} "
            f"{str(row['difference']):>12}  "
            f"{row['status']}"
        )


def print_summary(title, summary):
    print(f"\n{title}")
    print("-" * 90)
    print(
        f"{'ID':<8} {'Expected (INR)':>16} "
        f"{'Collected (INR)':>18} {'Variance (INR)':>16} "
        f"{'Transactions':>14}"
    )

    total_expected = Decimal("0.00")
    total_collected = Decimal("0.00")

    for key, data in sorted(summary.items()):
        expected = data["expected"]
        collected = data["collected"]
        variance = money(collected - expected)

        total_expected += expected
        total_collected += collected

        print(
            f"{key:<8} {str(money(expected)):>16} "
            f"{str(money(collected)):>18} "
            f"{str(variance):>16} "
            f"{data['transactions']:>14}"
        )

        if data.get("missing", 0):
            print(
                f"  Warning: {data['missing']} transaction(s) "
                "have missing collection data."
            )

    print("-" * 90)
    print(
        f"{'TOTAL':<8} {str(money(total_expected)):>16} "
        f"{str(money(total_collected)):>18} "
        f"{str(money(total_collected - total_expected)):>16}"
    )


# ----------------------------------------
# 5. EXPORT REPORT TO CSV
# ----------------------------------------

def export_report(results, filename="reconciliation_report.csv"):
    if not results:
        print("No results to export.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nReport exported to {filename}")


# ----------------------------------------
# 6. SAMPLE TRANSACTIONS
# ----------------------------------------

if __name__ == "__main__":

    transactions = [
        {
            "transaction_id": "TX001",
            "route_id": "R101",
            "category": "adult",
            "passengers": 1,
            "collected_amount": "30.00",
        },
        {
            "transaction_id": "TX002",
            "route_id": "R102",
            "category": "student",
            "passengers": 2,
            "collected_amount": "112.00",
        },
        {
            "transaction_id": "TX003",
            "route_id": "R103",
            "category": "senior",
            "passengers": 1,
            "collected_amount": "10.00",
        },
        {
            "transaction_id": "TX004",
            "route_id": "R104",
            "category": "adult",
            "passengers": 1,
            "collected_amount": "65.00",
        },
        {
            "transaction_id": "TX005",
            "route_id": "R101",
            "category": "child",
            "passengers": 1,
            "collected_amount": None,
        },
        {
            "transaction_id": "TX006",
            "route_id": "R102",
            "category": "adult",
            "passengers": 1,
            "collected_amount": "80.00",
        },
    ]

    results, route_summary, category_summary = (
        reconcile_transactions(transactions)
    )

    print_transaction_report(results)
    print_summary("ROUTE-WISE SUMMARY", route_summary)
    print_summary("CATEGORY-WISE SUMMARY", category_summary)
    export_report(results)
