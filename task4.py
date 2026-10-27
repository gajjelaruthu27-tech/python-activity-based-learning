
from dataclasses import dataclass
from typing import List


@dataclass
class Incident:
    incident_id: int
    description: str
    severity: str
    location: str
    frequency: int
    immediate_threat: bool = False
    score: int = 0
    priority: str = ""
    action: str = ""


# Predefined scoring rules
SEVERITY_POINTS = {
    "Critical": 5,
    "High": 4,
    "Medium": 3,
    "Low": 1
}

LOCATION_POINTS = {
    "Critical Area": 3,
    "High-Traffic Area": 2,
    "General Area": 1
}


def get_frequency_points(frequency: int) -> int:
    """Convert number of reports into frequency points."""
    if frequency >= 5:
        return 3
    elif frequency >= 3:
        return 2
    return 1


def classify_incident(incident: Incident) -> Incident:
    """Calculate score, assign priority, and recommend action."""

    incident.score = (
        SEVERITY_POINTS[incident.severity]
        + LOCATION_POINTS[incident.location]
        + get_frequency_points(incident.frequency)
    )

    # Immediate safety threats override the numerical score.
    if incident.immediate_threat:
        incident.priority = "P1 - IMMEDIATE ESCALATION"
        incident.action = (
            "Secure the area and notify campus emergency "
            "or facilities personnel immediately."
        )

    elif incident.score >= 9:
        incident.priority = "P1 - CRITICAL"
        incident.action = (
            "Immediate response and qualified inspection."
        )

    elif incident.score >= 7:
        incident.priority = "P2 - HIGH"
        incident.action = "Arrange urgent inspection and repair."

    elif incident.score >= 5:
        incident.priority = "P3 - MEDIUM"
        incident.action = "Schedule maintenance soon."

    else:
        incident.priority = "P4 - LOW"
        incident.action = "Add to the routine maintenance queue."

    return incident


def rank_incidents(incidents: List[Incident]) -> List[Incident]:
    """Rank incidents by priority, score, and severity."""

    priority_order = {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4
    }

    def sort_key(incident):
        priority_code = incident.priority.split(" - ")[0]
        return (
            priority_order[priority_code],
            -incident.score,
            -SEVERITY_POINTS[incident.severity]
        )

    return sorted(incidents, key=sort_key)


def generate_summary(incidents: List[Incident]) -> None:
    """Display ranked incidents and a priority summary."""

    print("\n" + "=" * 90)
    print(" SMART CAMPUS INCIDENT & MAINTENANCE PRIORITIZATION")
    print("=" * 90)

    print(
        f"{'Rank':<6}{'ID':<5}{'Incident':<32}"
        f"{'Score':<8}{'Priority':<28}"
    )
    print("-" * 90)

    for rank, incident in enumerate(incidents, start=1):
        print(
            f"{rank:<6}"
            f"{incident.incident_id:<5}"
            f"{incident.description[:30]:<32}"
            f"{incident.score:<8}"
            f"{incident.priority:<28}"
        )

    print("\nRECOMMENDED ACTIONS")
    print("-" * 90)

    for incident in incidents:
        print(f"\n#{incident.incident_id}: {incident.description}")
        print(f"Priority: {incident.priority}")
        print(f"Action: {incident.action}")

    # Count incidents by priority
    counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}

    for incident in incidents:
        code = incident.priority.split(" - ")[0]
        counts[code] += 1

    print("\n" + "=" * 40)
    print("PRIORITY SUMMARY")
    print("=" * 40)
    print(f"P1 - Critical / Immediate: {counts['P1']}")
    print(f"P2 - High:                 {counts['P2']}")
    print(f"P3 - Medium:               {counts['P3']}")
    print(f"P4 - Low:                  {counts['P4']}")
    print(f"Total incidents:           {len(incidents)}")


def main():
    # Hypothetical campus maintenance reports
    incidents = [
        Incident(
            1, "Exposed laboratory wiring",
            "Critical", "Critical Area", 5, True
        ),
        Incident(
            2, "Water leakage in main corridor",
            "High", "High-Traffic Area", 4
        ),
        Incident(
            3, "Repeated classroom AC failure",
            "Medium", "High-Traffic Area", 5
        ),
        Incident(
            4, "Broken library light",
            "Medium", "General Area", 3
        ),
        Incident(
            5, "Damaged common-area bench",
            "Low", "High-Traffic Area", 4
        ),
        Incident(
            6, "Loose office cabinet handle",
            "Low", "General Area", 1
        )
    ]

    # Classify every incident
    for incident in incidents:
        classify_incident(incident)

    # Rank and generate the summary
    ranked = rank_incidents(incidents)
    generate_summary(ranked)


if __name__ == "__main__":
    main()
