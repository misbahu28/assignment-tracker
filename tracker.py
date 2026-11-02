import argparse
import json
import sys
from datetime import date

DATA_FILE = "assignments.json"


def load_assignments():
    try:
        with open(DATA_FILE) as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_assignments(assignments):
    with open(DATA_FILE, "w") as file:
        json.dump(assignments, file, indent=2)


def get_due_date(assignment):
    return assignment["due"]


def list_assignments(week_only):
    assignments = sorted(load_assignments(), key=get_due_date)
    today = date.today()

    print("Upcoming assignments")
    print("--------------------")
    shown = 0
    for assignment in assignments:
        due = date.fromisoformat(assignment["due"])
        days_left = (due - today).days
        if days_left < 0:
            continue
        if week_only and days_left > 7:
            continue
        print(f"{assignment['course']}: {assignment['title']} - due {assignment['due']} ({days_left} days left)")
        shown += 1

    if shown == 0:
        print("Nothing due. Nice!")


def add_assignment(course, title, due):
    try:
        date.fromisoformat(due)
    except ValueError:
        print(f"Error: '{due}' is not a valid date. Use YYYY-MM-DD, like 2026-11-25.")
        sys.exit(1)

    assignments = load_assignments()
    assignments.append({"course": course, "title": title, "due": due})
    save_assignments(assignments)
    print(f"Added: {course}: {title} (due {due})")


def main():
    parser = argparse.ArgumentParser(description="Track your assignment deadlines.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="show upcoming assignments")
    list_parser.add_argument("--week", action="store_true", help="only show things due in the next 7 days")

    add_parser = subparsers.add_parser("add", help="add a new assignment")
    add_parser.add_argument("course", help='course code, like "PROG 101"')
    add_parser.add_argument("title", help="assignment name")
    add_parser.add_argument("due", help="due date as YYYY-MM-DD")

    args = parser.parse_args()

    if args.command == "list":
        list_assignments(args.week)
    elif args.command == "add":
        add_assignment(args.course, args.title, args.due)


if __name__ == "__main__":
    main()