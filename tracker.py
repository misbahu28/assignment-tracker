import argparse
import json
from datetime import date


def load_assignments():
    with open("assignments.json") as file:
        return json.load(file)


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


def main():
    parser = argparse.ArgumentParser(description="Track your assignment deadlines.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="show upcoming assignments")
    list_parser.add_argument("--week", action="store_true", help="only show things due in the next 7 days")

    args = parser.parse_args()

    if args.command == "list":
        list_assignments(args.week)


if __name__ == "__main__":
    main()