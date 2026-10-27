
from collections import defaultdict

# ==========================================
# DISASTER RELIEF SUPPLY ALLOCATION SYSTEM
# ==========================================

# Available stock in the central warehouse
stock = {
    "Water": 1000,
    "Food": 300,
    "Medical Kits": 100,
    "Shelter Kits": 150
}

# Area-wise requirements
requirements = {
    "Area A": {
        "Water": 600,
        "Food": 200,
        "Medical Kits": 50,
        "Shelter Kits": 80
    },
    "Area B": {
        "Water": 800,
        "Food": 250,
        "Medical Kits": 60,
        "Shelter Kits": 100
    },
    "Area C": {
        "Water": 400,
        "Food": 150,
        "Medical Kits": 40,
        "Shelter Kits": 50
    }
}

# Priority: 1 = highest urgency
priority = {
    "Area A": 1,
    "Area B": 2,
    "Area C": 3
}

# Allocation policy:
# "priority"      - Highest-priority areas first
# "proportional"  - Allocate proportionally to demand
POLICY = "priority"

# Initialize allocation records
allocation = {
    area: {item: 0 for item in stock}
    for area in requirements
}

remaining_stock = stock.copy()
unmet_demand = {
    area: demand.copy()
    for area, demand in requirements.items()
}


def allocate_priority():
    """Allocate each item to areas in priority order."""
    for area in sorted(requirements, key=lambda a: priority[a]):
        for item, demand in requirements[area].items():
            quantity = min(
                remaining_stock[item],
                demand
            )
            allocation[area][item] += quantity
            remaining_stock[item] -= quantity
            unmet_demand[area][item] -= quantity


def allocate_proportional():
    """Allocate each item's stock proportionally to demand."""
    for item, available in stock.items():
        total_demand = sum(
            requirements[area].get(item, 0)
            for area in requirements
        )

        if total_demand == 0:
            continue

        # Initial proportional allocation using whole units
        assigned = 0
        areas = list(requirements)

        for area in areas:
            demand = requirements[area].get(item, 0)
            quantity = min(
                demand,
                (available * demand) // total_demand
            )
            allocation[area][item] = quantity
            assigned += quantity

        # Distribute leftover units without exceeding demand
        left = available - assigned

        for area in sorted(areas, key=lambda a: priority[a]):
            demand = requirements[area].get(item, 0)
            extra_capacity = demand - allocation[area][item]
            extra = min(left, extra_capacity)
            allocation[area][item] += extra
            left -= extra

            if left == 0:
                break

        remaining_stock[item] = available - sum(
            allocation[area][item] for area in areas
        )

        for area in areas:
            unmet_demand[area][item] = (
                requirements[area].get(item, 0)
                - allocation[area][item]
            )


# Run selected policy
if POLICY == "priority":
    allocate_priority()
elif POLICY == "proportional":
    allocate_proportional()
else:
    raise ValueError("Unknown allocation policy")


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\nDISASTER RELIEF SUPPLY ALLOCATION REPORT")
print("=" * 60)

for area in requirements:
    print(f"\n{area} (Priority {priority[area]})")
    print("-" * 45)

    for item in stock:
        demand = requirements[area].get(item, 0)
        allocated = allocation[area][item]
        unmet = unmet_demand[area][item]

        fulfillment = (
            allocated / demand * 100 if demand > 0 else 100
        )

        print(
            f"{item:15} | Required: {demand:4} | "
            f"Allocated: {allocated:4} | "
            f"Unmet: {unmet:4} | "
            f"Fulfilled: {fulfillment:6.2f}%"
        )

print("\n" + "=" * 60)
print("CENTRAL WAREHOUSE SUMMARY")
print("=" * 60)

for item in stock:
    total_demand = sum(
        requirements[area].get(item, 0)
        for area in requirements
    )
    total_allocated = sum(
        allocation[area][item] for area in requirements
    )
    total_unmet = sum(
        unmet_demand[area][item] for area in requirements
    )

    print(f"\nItem: {item}")
    print(f"  Initial stock   : {stock[item]}")
    print(f"  Total demand    : {total_demand}")
    print(f"  Total allocated : {total_allocated}")
    print(f"  Remaining stock : {remaining_stock[item]}")
    print(f"  Unmet demand    : {total_unmet}")

print("\nAllocation completed.")
