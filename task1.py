
# Comprehensive Smart Campus Management Simulation

students = []
attendance_records = []
marks_records = []
event_registrations = []
resource_allocations = []

# Tuples: (event_id, event_name, date)
events = [
    (1, "Tech Fest", "10-11-2026"),
    (2, "Sports Day", "15-11-2026"),
    (3, "Cultural Fest", "20-11-2026")
]

# Tuples: (resource_id, resource_name, capacity)
resources = [
    (1, "Seminar Hall", 100),
    (2, "Computer Lab", 40),
    (3, "Auditorium", 200)
]


def find_student(roll_no):
    for student in students:
        if student[0] == roll_no:
            return student
    return None


def add_student():
    roll_no = input("Enter roll number: ")

    if find_student(roll_no) is not None:
        print("Student already exists!")
        return

    name = input("Enter student name: ")
    department = input("Enter department: ")
    year = int(input("Enter year of study: "))

    if year < 1 or year > 4:
        print("Invalid year!")
        return

    students.append([roll_no, name, department, year])
    print("Student record added successfully.")


def display_students():
    if not students:
        print("No student records found.")
        return

    print("\n--- Student Records ---")
    for roll_no, name, department, year in students:
        print(
            "Roll No:", roll_no,
            "| Name:", name,
            "| Department:", department,
            "| Year:", year
        )


def mark_attendance():
    roll_no = input("Enter student roll number: ")

    if find_student(roll_no) is None:
        print("Student not found!")
        return

    date = input("Enter date (DD-MM-YYYY): ")
    status = input("Enter attendance (P/A): ").upper()

    if status not in ("P", "A"):
        print("Invalid attendance status!")
        return

    attendance_records.append([roll_no, date, status])
    print("Attendance recorded successfully.")


def display_attendance():
    roll_no = input("Enter roll number: ")
    found = False
    present = 0
    total = 0

    print("\n--- Attendance Report ---")

    for record_roll, date, status in attendance_records:
        if record_roll == roll_no:
            print(date, "-", "Present" if status == "P" else "Absent")
            total += 1

            if status == "P":
                present += 1

            found = True

    if found:
        percentage = (present / total) * 100
        print("Present:", present)
        print("Total classes:", total)
        print("Attendance percentage:", round(percentage, 2), "%")
    else:
        print("No attendance records found.")


def enter_marks():
    roll_no = input("Enter student roll number: ")

    if find_student(roll_no) is None:
        print("Student not found!")
        return

    subject = input("Enter subject name: ")

    try:
        marks = float(input("Enter marks out of 100: "))
    except ValueError:
        print("Marks must be numeric!")
        return

    if marks < 0 or marks > 100:
        print("Marks must be between 0 and 100.")
        return

    marks_records.append([roll_no, subject, marks])
    print("Marks recorded successfully.")


def display_marks():
    roll_no = input("Enter roll number: ")
    total_marks = 0
    count = 0

    print("\n--- Marks Report ---")

    for record_roll, subject, marks in marks_records:
        if record_roll == roll_no:
            print(subject, ":", marks, "/ 100")
            total_marks += marks
            count += 1

    if count > 0:
        average = total_marks / count

        if average >= 90:
            grade = "A+"
        elif average >= 80:
            grade = "A"
        elif average >= 70:
            grade = "B"
        elif average >= 60:
            grade = "C"
        elif average >= 50:
            grade = "D"
        else:
            grade = "F"

        print("Average marks:", round(average, 2))
        print("Grade:", grade)
    else:
        print("No marks records found.")


def display_events():
    print("\n--- Available Campus Events ---")

    for event_id, event_name, date in events:
        print(event_id, "-", event_name, "| Date:", date)


def register_event():
    roll_no = input("Enter student roll number: ")

    if find_student(roll_no) is None:
        print("Student not found!")
        return

    display_events()

    try:
        event_id = int(input("Enter event ID: "))
    except ValueError:
        print("Enter a valid event ID!")
        return

    selected_event = None

    for eid, event_name, date in events:
        if eid == event_id:
            selected_event = (eid, event_name, date)
            break

    if selected_event is None:
        print("Invalid event ID!")
        return

    for registered_roll, registered_event in event_registrations:
        if registered_roll == roll_no and registered_event == event_id:
            print("Already registered for this event!")
            return

    event_registrations.append((roll_no, event_id))
    print("Successfully registered for", selected_event[1])


def allocate_resource():
    roll_no = input("Enter student roll number: ")

    if find_student(roll_no) is None:
        print("Student not found!")
        return

    print("\n--- Available Resources ---")

    for resource_id, resource_name, capacity in resources:
        print(
            resource_id, "-", resource_name,
            "| Capacity:", capacity
        )

    try:
        resource_id = int(input("Enter resource ID: "))
        people = int(input("Enter number of people: "))
    except ValueError:
        print("Enter valid numeric values!")
        return

    selected_resource = None

    for rid, resource_name, capacity in resources:
        if rid == resource_id:
            selected_resource = (rid, resource_name, capacity)
            break

    if selected_resource is None:
        print("Invalid resource ID!")
        return

    rid, resource_name, capacity = selected_resource

    if people <= 0:
        print("Number of people must be positive.")
    elif people > capacity:
        print("Requested number exceeds resource capacity!")
    else:
        resource_allocations.append(
            [roll_no, resource_name, people]
        )
        print("Resource allocated:", resource_name)


def summary_report():
    print("\n========== CAMPUS SUMMARY ==========")
    print("Total students:", len(students))
    print("Attendance entries:", len(attendance_records))
    print("Marks entries:", len(marks_records))
    print("Event registrations:", len(event_registrations))
    print("Resource allocations:", len(resource_allocations))

    print("\n--- Student-wise Summary ---")

    for roll_no, name, department, year in students:
        present = 0
        total = 0
        student_marks = []

        for record_roll, date, status in attendance_records:
            if record_roll == roll_no:
                total += 1
                if status == "P":
                    present += 1

        for record_roll, subject, marks in marks_records:
            if record_roll == roll_no:
                student_marks.append(marks)

        attendance_percentage = (
            (present / total) * 100 if total > 0 else 0
        )

        average_marks = (
            sum(student_marks) / len(student_marks)
            if student_marks else 0
        )

        print("\nName:", name, "| Roll No:", roll_no)
        print("Department:", department, "| Year:", year)
        print("Attendance:", round(attendance_percentage, 2), "%")
        print("Average marks:", round(average_marks, 2))

        if total > 0 and attendance_percentage < 75:
            print("Warning: Attendance below 75%!")

    print("\n--- Event Registration Summary ---")

    for event_id, event_name, date in events:
        count = 0

        for roll_no, registered_event in event_registrations:
            if registered_event == event_id:
                count += 1

        print(event_name, ":", count, "registrations")

    print("=====================================")


def main():
    while True:
        print("\n===== SMART CAMPUS MANAGEMENT =====")
        print("1. Add Student")
        print("2. Display Students")
        print("3. Mark Attendance")
        print("4. View Attendance")
        print("5. Enter Marks")
        print("6. View Marks")
        print("7. View Events")
        print("8. Register for Event")
        print("9. Allocate Resource")
        print("10. Summary Report")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            display_students()
        elif choice == "3":
            mark_attendance()
        elif choice == "4":
            display_attendance()
        elif choice == "5":
            enter_marks()
        elif choice == "6":
            display_marks()
        elif choice == "7":
            display_events()
        elif choice == "8":
            register_event()
        elif choice == "9":
            allocate_resource()
        elif choice == "10":
            summary_report()
        elif choice == "0":
            print("Thank you for using Smart Campus Management!")
            break
        else:
            print("Invalid choice! Please try again.")


main()
