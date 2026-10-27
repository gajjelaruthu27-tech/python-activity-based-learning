
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Any


# Expected registration format:
# REG20260001|Rahul Kumar|rahul@example.com|9876543210

FIELD_NAMES = ["registration_id", "name", "email", "phone"]

FIELD_LENGTHS = {
    "registration_id": (8, 12),
    "name": (2, 50),
    "email": (5, 100),
    "phone": (10, 10),
}

REGISTRATION_PATTERN = re.compile(r"^REG\d{8,}$")
EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)
PHONE_PATTERN = re.compile(r"^\d{10}$")


@dataclass
class RegistrationResult:
    record_number: int
    raw_record: str
    extracted: Dict[str, str] = field(default_factory=dict)
    errors: List[Dict[str, str]] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


class RegistrationAnalyzer:
    def __init__(self):
        self.results: List[RegistrationResult] = []

    def parse(self, raw_record: str, record_number: int):
        result = RegistrationResult(
            record_number=record_number,
            raw_record=raw_record
        )

        # 1. Validate the input itself
        if not isinstance(raw_record, str):
            result.errors.append({
                "code": "INVALID_TYPE",
                "message": "Record must be a string."
            })
            self.results.append(result)
            return result

        if not raw_record.strip():
            result.errors.append({
                "code": "EMPTY_RECORD",
                "message": "Registration record is empty."
            })
            self.results.append(result)
            return result

        # 2. Split the structured registration string
        parts = raw_record.strip().split("|")

        if len(parts) != len(FIELD_NAMES):
            result.errors.append({
                "code": "FIELD_COUNT_MISMATCH",
                "message": (
                    f"Expected {len(FIELD_NAMES)} fields, "
                    f"received {len(parts)}."
                )
            })
            self.results.append(result)
            return result

        # 3. Extract fields
        result.extracted = {
            name: value.strip()
            for name, value in zip(FIELD_NAMES, parts)
        }

        # 4. Validate individual fields
        for name, value in result.extracted.items():
            minimum, maximum = FIELD_LENGTHS[name]

            if not value:
                result.errors.append({
                    "code": "MISSING_FIELD",
                    "field": name,
                    "message": f"{name} cannot be empty."
                })
                continue

            if not minimum <= len(value) <= maximum:
                result.errors.append({
                    "code": "INVALID_LENGTH",
                    "field": name,
                    "message": (
                        f"{name} must contain {minimum}-{maximum} "
                        f"characters; received {len(value)}."
                    )
                })

        # 5. Validate field formats
        reg_id = result.extracted["registration_id"]
        if reg_id and not REGISTRATION_PATTERN.fullmatch(reg_id):
            result.errors.append({
                "code": "INVALID_REGISTRATION_FORMAT",
                "field": "registration_id",
                "message": "ID must start with REG followed by digits."
            })

        email = result.extracted["email"]
        if email and not EMAIL_PATTERN.fullmatch(email):
            result.errors.append({
                "code": "INVALID_EMAIL",
                "field": "email",
                "message": "Email address has an invalid format."
            })

        phone = result.extracted["phone"]
        if phone and not PHONE_PATTERN.fullmatch(phone):
            result.errors.append({
                "code": "INVALID_PHONE",
                "field": "phone",
                "message": "Phone must contain exactly 10 digits."
            })

        self.results.append(result)
        return result

    def analyze_all(self, records: List[str]):
        self.results = []

        # Parse each record
        for index, record in enumerate(records, start=1):
            self.parse(record, index)

        # 6. Detect duplicate registration IDs
        id_occurrences = Counter(
            result.extracted["registration_id"]
            for result in self.results
            if result.extracted.get("registration_id")
        )

        for result in self.results:
            reg_id = result.extracted.get("registration_id", "")

            if reg_id and id_occurrences[reg_id] > 1:
                result.errors.append({
                    "code": "DUPLICATE_REGISTRATION_ID",
                    "field": "registration_id",
                    "message": f"Registration ID '{reg_id}' occurs "
                               f"{id_occurrences[reg_id]} times."
                })

        return self.results

    def report(self):
        valid_count = sum(r.valid for r in self.results)
        invalid_count = len(self.results) - valid_count

        print("\n" + "=" * 65)
        print("       REGISTRATION RECORD ANALYSIS REPORT")
        print("=" * 65)

        for result in self.results:
            status = "VALID" if result.valid else "INVALID"

            print(f"\nRecord #{result.record_number}: {status}")
            print(f"Raw input: {result.raw_record}")

            if result.extracted:
                print("Extracted fields:")
                for key, value in result.extracted.items():
                    print(f"  {key}: {value}")

            if result.errors:
                print("Errors:")
                for error in result.errors:
                    field_name = error.get("field", "record")
                    print(
                        f"  [{error['code']}] "
                        f"{field_name}: {error['message']}"
                    )

        error_counts = Counter(
            error["code"]
            for result in self.results
            for error in result.errors
        )

        print("\n" + "=" * 65)
        print("SUMMARY")
        print("=" * 65)
        print(f"Total records : {len(self.results)}")
        print(f"Valid records : {valid_count}")
        print(f"Invalid records: {invalid_count}")
        print("\nError classifications:")

        if error_counts:
            for code, count in sorted(error_counts.items()):
                print(f"  {code}: {count}")
        else:
            print("  No errors found.")

        return {
            "total": len(self.results),
            "valid": valid_count,
            "invalid": invalid_count,
            "error_counts": dict(error_counts),
        }


# ---------------- MAIN PROGRAM ----------------

if __name__ == "__main__":
    registration_records = [
        "REG20260001|Rahul Kumar|rahul@example.com|9876543210",
        "REG20260002|Priya Sharma|priya@example.com|9123456789",
        "REG20260001|Amit Verma|amit@example.com|9988776655",
        "REG123|John|invalid-email|12345",
        "REG20260005||test@example.com|9876543210",
        "REG20260006|Anita Rao|anita@example.com|9876543210",
        "REG20260007|Kiran Das|kiran@example.com",
        "",
    ]

    analyzer = RegistrationAnalyzer()
    analyzer.analyze_all(registration_records)
    summary = analyzer.report()
