
# University Academic Progression Audit System

# Student: [Student ID, Name, Current Semester]
students = [
    ["S101", "Ananya", 2],
    ["S102", "Rahul", 2],
    ["S103", "Priya", 2]
]

# Subjects: (Subject Code, Subject Name, Semester, Prerequisite Code)
subjects = [
    ("CS101", "Programming", 1, None),
    ("MA101", "Mathematics", 1, None),
    ("CS201", "Data Structures", 2, "CS101"),
    ("MA201", "Statistics", 2, "MA101"),
    ("CS301", "Algorithms", 3, "CS201")
]

# Marks: [Student ID, Subject Code, Marks out of 100]
marks_records = [
    ["S101", "CS101", 75],
    ["S101", "MA101", 68],
    ["S101", "CS201", 72],
    ["S101", "MA201", 45],

    ["S102", "CS101", 35],
    ["S102", "MA101", 62],
    ["S102", "CS201", 55],
    ["S102", "MA201", 70],

    ["S103", "CS101", 80],
    ["S103", "MA101", 85],
    ["S103", "CS201", 40],
    ["S103", "MA201", 75]
]

# Attendance: [Student ID, Subject Code, Attendance Percentage]
attendance_records = [
    ["S101", "CS201", 85],
    ["S101", "MA201", 72],
    ["S102", "CS201", 80],
    ["S102", "MA201", 90],
    ["S103", "CS201", 68],
    ["S103", "MA201", 88]
]

PASS_MARKS = 40
MIN_ATTENDANCE = 75


def find_student(student_id):
    for student in students:
        if student[0] == student_id:
            return student
    return None


def find_subject(subject_code):
    for subject in subjects:
        if subject[0] == subject_code:
            return subject
    return None


def get_marks(student_id, subject_code):
    for sid, code, score in marks_records:
        if sid == student_id and code == subject_code:
            return score
    return None


def get_attendance(student_id, subject_code):
    for sid, code, percentage in attendance_records:
        if sid == student_id and code == subject_code:
            return percentage
    return None


def has_passed(student_id, subject_code):
    score = get_marks(student_id, subject_code)
    return score is not None and score >= PASS_MARKS


def audit_student(student):
    student_id, name, semester = student
    outstanding = []
    passed_count = 0
    total_subjects = 0

    print("\n========================================")
    print("ACADEMIC PROGRESSION AUDIT")
    print("Student ID:", student_id)
    print("Student Name:", name)
    print("Current Semester:", semester)
    print("========================================")

    for code, subject_name, subject_sem, prerequisite in subjects:
        # Audit subjects belonging to the current semester.
        if subject_sem != semester:
            continue

        total_subjects += 1
        score = get_marks(student_id, code)
        attendance = get_attendance(student_id, code)

        print("\nSubject:", subject_name, "(" + code + ")")

        # Check marks and pass conditions.
        if score is None:
            print("Marks: Not recorded")
            outstanding.append(subject_name + ": Marks missing")
        else:
            print("Marks:", score)

            if score < PASS_MARKS:
                print("Status: FAIL")
                outstanding.append(subject_name + ": Pass marks required")
            else:
                print("Status: PASS")
                passed_count += 1

        # Check attendance.
        if attendance is None:
            print("Attendance: Not recorded")
            outstanding.append(subject_name + ": Attendance missing")
        else:
            print("Attendance:", attendance, "%")

            if attendance < MIN_ATTENDANCE:
                print("Attendance status: INSUFFICIENT")
                outstanding.append(
                    subject_name + ": Attendance below 75%"
                )
            else:
                print("Attendance status: SATISFACTORY")

        # Check prerequisite completion.
        if prerequisite is not None:
            if not has_passed(student_id, prerequisite):
                prerequisite_subject = find_subject(prerequisite)

                if prerequisite_subject is not None:
                    prerequisite_name = prerequisite_subject[1]
                else:
                    prerequisite_name = prerequisite

                print(
                    "Prerequisite incomplete:",
                    prerequisite_name
                )
                outstanding.append(
                    subject_name + ": Prerequisite " +
                    prerequisite_name + " incomplete"
                )
            else:
                print("Prerequisite: COMPLETED")

    # Audit all prerequisites for the next semester.
    next_semester = semester + 1

    print("\n--- Next Semester Prerequisite Audit ---")

    for code, subject_name, subject_sem, prerequisite in subjects:
        if subject_sem == next_semester and prerequisite is not None:
            if not has_passed(student_id, prerequisite):
                prereq_subject = find_subject(prerequisite)
                prereq_name = (
                    prereq_subject[1]
                    if prereq_subject is not None
                    else prerequisite
                )

                message = (
                    "Next-semester prerequisite outstanding: "
                    + prereq_name
                )

                if message not in outstanding:
                    outstanding.append(message)

                print(message)
            else:
                print(subject_name, "-", "Prerequisite completed")

    # Determine progression eligibility.
    current_semester_eligible = True

    for code, subject_name, subject_sem, prerequisite in subjects:
        if subject_sem != semester:
            continue

        score = get_marks(student_id, code)
        attendance = get_attendance(student_id, code)

        if score is None or score < PASS_MARKS:
            current_semester_eligible = False

        if attendance is None or attendance < MIN_ATTENDANCE:
            current_semester_eligible = False

        if prerequisite is not None:
            if not has_passed(student_id, prerequisite):
                current_semester_eligible = False

    print("\n========== AUDIT RESULT ==========")
    print("Subjects audited:", total_subjects)
    print("Subjects passed:", passed_count)

    if current_semester_eligible:
        print("Progression status: ELIGIBLE")
        print("Student meets the configured audit conditions.")
    else:
        print("Progression status: NOT ELIGIBLE")
        print("Outstanding requirements:", len(outstanding))

    if outstanding:
        print("\nOutstanding Requirements:")
        for item in outstanding:
            print("-", item)
    else:
        print("No outstanding requirements.")

    print("==================================")


def add_marks():
    student_id = input("Enter student ID: ").upper()

    if find_student(student_id) is None:
        print("Student not found!")
        return

    code = input("Enter subject code: ").upper()

    if find_subject(code) is None:
        print("Subject not found!")
        return

    try:
        score = float(input("Enter marks out of 100: "))
    except ValueError:
        print("Invalid marks!")
        return

    if score < 0 or score > 100:
        print("Marks must be between 0 and 100.")
        return

    for record in marks_records:
        if record[0] == student_id and record[1] == code:
            record[2] = score
            print("Marks updated successfully.")
            return

    marks_records.append([student_id, code, score])
    print("Marks added successfully.")


def update_attendance():
    student_id = input("Enter student ID: ").upper()

    if find_student(student_id) is None:
        print("Student not found!")
        return

    code = input("Enter subject code: ").upper()

    if find_subject(code) is None:
        print("Subject not found!")
        return

    try:
        percentage = float(input("Enter attendance percentage: "))
    except ValueError:
        print("Invalid percentage!")
        return

    if percentage < 0 or percentage > 100:
        print("Attendance must be between 0 and 100.")
        return

    for record in attendance_records:
        if record[0] == student_id and record[1] == code:
            record[2] = percentage
            print("Attendance updated successfully.")
            return

    attendance_records.append([student_id, code, percentage])
    print("Attendance added successfully.")


def audit_all_students():
    for student in students:
        audit_student(student)


def display_students():
    print("\n--- Registered Students ---")

    for student_id, name, semester in students:
        print(
            "ID:", student_id,
            "| Name:", name,
            "| Semester:", semester
        )


def main():
    while True:
        print("\n===== UNIVERSITY PROGRESSION AUDIT =====")
        print("1. Display Students")
        print("2. Audit Individual Student")
        print("3. Audit All Students")
        print("4. Add or Update Marks")
        print("5. Add or Update Attendance")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            display_students()

        elif choice == "2":
            student_id = input("Enter student ID: ").upper()
            student = find_student(student_id)

            if student is not None:
                audit_student(student)
            else:
                print("Student not found!")

        elif choice == "3":
            audit_all_students()

        elif choice == "4":
            add_marks()

        elif choice == "5":
            update_attendance()

        elif choice == "0":
            print("Exiting Academic Progression Audit System.")
            break

        else:
            print("Invalid choice! Please try again.")


main()
s