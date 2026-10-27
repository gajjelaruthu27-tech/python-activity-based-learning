
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Branch:
    name: str
    demand: int
    borrowing_rate: float
    priority: int
    allocation: int = 0

    @property
    def unmet_demand(self):
        return max(0, self.demand - self.allocation)


def distribute_books(
    book_title: str,
    available_copies: int,
    branches: List[Branch]
) -> Dict:
    """
    Allocation priority:
    1. Higher branch priority first (1 is highest).
    2. Higher borrowing rate first.
    3. Higher demand first.
    4. Branch name alphabetically as tie-breaker.

    Each branch receives copies until its demand is met
    or the available stock is exhausted.
    """

    if available_copies < 0:
        raise ValueError("Available copies cannot be negative.")

    for branch in branches:
        if branch.demand < 0:
            raise ValueError(
                f"Demand cannot be negative: {branch.name}"
            )
        if branch.priority < 1:
            raise ValueError(
                f"Priority must be 1 or greater: {branch.name}"
            )
        if not 0 <= branch.borrowing_rate <= 1:
            raise ValueError(
                f"Borrowing rate must be between 0 and 1: "
                f"{branch.name}"
            )
        branch.allocation = 0

    # Sort branches using the specified priority rules.
    ranked_branches = sorted(
        branches,
        key=lambda b: (
            b.priority,
            -b.borrowing_rate,
            -b.demand,
            b.name.lower()
        )
    )

    remaining = available_copies

    # Allocate stock in priority order.
    for branch in ranked_branches:
        allocated = min(branch.demand, remaining)
        branch.allocation = allocated
        remaining -= allocated

    total_demand = sum(b.demand for b in branches)
    total_allocated = sum(b.allocation for b in branches)
    total_unmet = sum(b.unmet_demand for b in branches)

    report = {
        "book": book_title,
        "available": available_copies,
        "total_demand": total_demand,
        "allocated": total_allocated,
        "unmet_demand": total_unmet,
        "unused_stock": remaining,
        "branches": ranked_branches
    }

    return report


def display_report(report: Dict):
    print("\n" + "=" * 88)
    print(f"RESOURCE DISTRIBUTION REPORT: {report['book']}")
    print("=" * 88)
    print(f"Available copies : {report['available']}")
    print(f"Total demand     : {report['total_demand']}")
    print(f"Total allocated  : {report['allocated']}")
    print(f"Unmet demand     : {report['unmet_demand']}")
    print(f"Unused stock     : {report['unused_stock']}")
    print("-" * 88)

    print(
        f"{'Branch':<15}"
        f"{'Priority':>10}"
        f"{'Demand':>10}"
        f"{'Borrow %':>12}"
        f"{'Allocated':>12}"
        f"{'Unmet':>10}"
    )
    print("-" * 88)

    for b in report["branches"]:
        print(
            f"{b.name:<15}"
            f"{b.priority:>10}"
            f"{b.demand:>10}"
            f"{b.borrowing_rate * 100:>11.1f}%"
            f"{b.allocation:>12}"
            f"{b.unmet_demand:>10}"
        )

    if report["total_demand"] > 0:
        fulfillment = (
            report["allocated"] / report["total_demand"]
        ) * 100
    else:
        fulfillment = 100.0

    print("-" * 88)
    print(f"Demand fulfillment: {fulfillment:.2f}%")
    print("=" * 88)


def main():
    # Sample library data.
    # Priority 1 is the highest priority.
    books = {
        "Python Programming": {
            "available": 50,
            "branches": [
                Branch("Central", 30, 0.90, 1),
                Branch("North", 25, 0.75, 2),
                Branch("South", 20, 0.85, 1),
                Branch("East", 15, 0.60, 3),
            ]
        },
        "Data Structures": {
            "available": 35,
            "branches": [
                Branch("Central", 15, 0.80, 1),
                Branch("North", 20, 0.90, 1),
                Branch("South", 18, 0.70, 2),
                Branch("East", 12, 0.65, 3),
            ]
        }
    }

    all_reports = []

    for title, data in books.items():
        report = distribute_books(
            title,
            data["available"],
            data["branches"]
        )
        display_report(report)
        all_reports.append(report)

    # Overall summary across all books.
    print("\nOVERALL LIBRARY SUMMARY")
    print("-" * 45)

    total_available = sum(r["available"] for r in all_reports)
    total_demand = sum(r["total_demand"] for r in all_reports)
    total_allocated = sum(r["allocated"] for r in all_reports)
    total_unmet = sum(r["unmet_demand"] for r in all_reports)

    print(f"Total available copies : {total_available}")
    print(f"Total borrowing demand : {total_demand}")
    print(f"Total copies allocated : {total_allocated}")
    print(f"Total unmet demand     : {total_unmet}")

    fulfillment = (
        100 * total_allocated / total_demand
        if total_demand else 100.0
    )
    print(f"Overall fulfillment    : {fulfillment:.2f}%")


if __name__ == "__main__":
    main()
