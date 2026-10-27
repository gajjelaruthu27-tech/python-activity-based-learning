
from dataclasses import dataclass
from math import ceil, floor
from typing import Dict, List
import json


@dataclass
class Material:
    name: str
    available: float
    per_unit: float


@dataclass
class ProductionOrder:
    order_id: str
    demand: int
    priority: int = 1


@dataclass
class QualityData:
    inspected: int
    defects: int
    max_defect_rate: float  # Percentage, e.g. 2.0 means 2%


class IntegratedManufacturingPlanner:
    def __init__(
        self,
        materials: List[Material],
        production_capacity: int,
        orders: List[ProductionOrder],
        quality: QualityData,
    ):
        self.materials = materials
        self.capacity = production_capacity
        self.orders = orders
        self.quality = quality

        self.validate_inputs()

    def validate_inputs(self):
        if self.capacity < 0:
            raise ValueError("Production capacity cannot be negative.")

        if any(m.available < 0 or m.per_unit <= 0
               for m in self.materials):
            raise ValueError(
                "Material inventory must be nonnegative and "
                "per-unit requirements must be positive."
            )

        if any(o.demand < 0 or o.priority < 1 for o in self.orders):
            raise ValueError("Invalid order demand or priority.")

        if (
            self.quality.inspected < 0
            or self.quality.defects < 0
            or self.quality.defects > self.quality.inspected
        ):
            raise ValueError("Invalid inspection or defect counts.")

        if not 0 <= self.quality.max_defect_rate <= 100:
            raise ValueError("Defect limit must be between 0 and 100.")

    def analyze_quality(self) -> dict:
        inspected = self.quality.inspected
        defects = self.quality.defects
        defect_rate = (
            defects / inspected * 100 if inspected else 0.0
        )
        quality_violation = (
            defect_rate > self.quality.max_defect_rate
        )

        return {
            "inspected_units": inspected,
            "defect_count": defects,
            "good_units": inspected - defects,
            "defect_rate_percent": round(defect_rate, 2),
            "maximum_allowed_defect_rate_percent":
                self.quality.max_defect_rate,
            "quality_violation": quality_violation,
            "status": (
                "VIOLATION" if quality_violation
                else "PASS"
            ),
        }

    def analyze_materials(self, planned_units: int) -> dict:
        results = {}
        max_units_by_material = []

        for material in self.materials:
            required = planned_units * material.per_unit
            shortage = max(0.0, required - material.available)
            surplus = max(0.0, material.available - required)

            max_units = floor(
                material.available / material.per_unit
            )
            max_units_by_material.append(max_units)

            results[material.name] = {
                "available": material.available,
                "required": round(required, 3),
                "shortage": round(shortage, 3),
                "surplus": round(surplus, 3),
                "maximum_units_supported": max_units,
                "status": "SHORTAGE" if shortage > 0 else "OK",
            }

        return {
            "materials": results,
            "maximum_units_from_materials": (
                min(max_units_by_material)
                if max_units_by_material else 0
            ),
        }

    def plan(self) -> dict:
        quality_report = self.analyze_quality()
        defect_rate = quality_report["defect_rate_percent"] / 100

        total_demand = sum(order.demand for order in self.orders)

        # Sort orders by priority (1 = highest), then order ID.
        sorted_orders = sorted(
            self.orders,
            key=lambda order: (order.priority, order.order_id)
        )

        # Calculate gross production needed to deliver enough
        # good units at the observed historical defect rate.
        if total_demand == 0:
            required_gross = 0
        elif defect_rate >= 1:
            required_gross = None
        else:
            required_gross = ceil(total_demand / (1 - defect_rate))

        target = required_gross if required_gross is not None else 0
        material_report = self.analyze_materials(target)

        material_limit = material_report[
            "maximum_units_from_materials"
        ]
        feasible_gross = min(self.capacity, material_limit)

        # Allocate expected good output to orders by priority.
        expected_good = floor(feasible_gross * (1 - defect_rate))
        remaining_good = expected_good
        order_results = []

        for order in sorted_orders:
            fulfilled = min(order.demand, remaining_good)
            remaining_good -= fulfilled

            order_results.append({
                "order_id": order.order_id,
                "priority": order.priority,
                "demand": order.demand,
                "expected_good_units_allocated": fulfilled,
                "unfulfilled_demand": order.demand - fulfilled,
                "status": (
                    "FULFILLED"
                    if fulfilled == order.demand
                    else "PARTIAL" if fulfilled > 0
                    else "UNFULFILLED"
                ),
            })

        # Material requirements are recalculated for the actual
        # feasible production plan.
        actual_materials = self.analyze_materials(feasible_gross)

        shortages = {
            name: data["shortage"]
            for name, data in actual_materials["materials"].items()
            if data["shortage"] > 0
        }

        total_unfulfilled = sum(
            item["unfulfilled_demand"] for item in order_results
        )

        recommendations = []

        if shortages:
            recommendations.append(
                "Procure the identified material shortages "
                "before increasing production."
            )

        if feasible_gross < target:
            recommendations.append(
                "Production is constrained by available materials "
                "or production capacity."
            )

        if quality_report["quality_violation"]:
            recommendations.append(
                "Investigate defects and implement corrective "
                "actions before releasing affected products."
            )

        if total_unfulfilled > 0:
            recommendations.append(
                "Reschedule production, add capacity, or revise "
                "delivery commitments for unfulfilled demand."
            )

        if not recommendations:
            recommendations.append(
                "Current production plan can meet demand under "
                "the estimated yield and quality assumptions."
            )

        return {
            "production_summary": {
                "total_order_demand": total_demand,
                "required_gross_production": required_gross,
                "production_capacity": self.capacity,
                "material_limited_capacity": material_limit,
                "feasible_gross_production": feasible_gross,
                "expected_good_units": expected_good,
                "expected_defective_units": (
                    feasible_gross - expected_good
                ),
                "unfulfilled_demand": total_unfulfilled,
                "production_feasible": (
                    required_gross is not None
                    and feasible_gross >= required_gross
                ),
            },
            "material_analysis": actual_materials["materials"],
            "quality_analysis": quality_report,
            "order_analysis": order_results,
            "recommendations": recommendations,
        }


def main():
    # Example input data: replace these values with plant data.
    materials = [
        Material("Steel", available=500, per_unit=2.0),
        Material("Plastic", available=300, per_unit=1.0),
        Material("Copper", available=180, per_unit=0.5),
    ]

    orders = [
        ProductionOrder("ORD-101", demand=100, priority=1),
        ProductionOrder("ORD-102", demand=120, priority=2),
        ProductionOrder("ORD-103", demand=80, priority=3),
    ]

    quality = QualityData(
        inspected=200,
        defects=8,
        max_defect_rate=2.0,
    )

    planner = IntegratedManufacturingPlanner(
        materials=materials,
        production_capacity=350,
        orders=orders,
        quality=quality,
    )

    report = planner.plan()

    print("INTEGRATED MANUFACTURING PRODUCTION REPORT")
    print("=" * 45)
    print(json.dumps(report, indent=4))

    # Save the report for downstream systems.
    with open("production_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\nReport saved to production_report.json"


if __name__ == "__main__":
    main()
