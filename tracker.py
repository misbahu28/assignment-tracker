import argparse
import json
import sys
import canvas
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


def days_until(assignment, today):
    due = date.fromisoformat(assignment["due"])
    return (due - today).days


def filter_upcoming(assignments, today, week_only):
    upcoming = []
    for assignment in sorted(assignments, key=get_due_date):
        days_left = days_until(assignment, today)
        if days_left < 0:
            continue
        if week_only and days_left > 7:
            continue
        upcoming.append(assignment)
    return upcoming


def remove_by_title(assignments, title):
    return [a for a in assignments if a["title"].lower() != title.lower()]


def list_assignments(week_only):
    today = date.today()
    upcoming = filter_upcoming(load_assignments(), today, week_only)

    print("Upcoming assignments")
    print("--------------------")
    for assignment in upcoming:
        days_left = days_until(assignment, today)
        print(f"{assignment['course']}: {assignment['title']} - due {assignment['due']} ({days_left} days left)")

    if not upcoming:
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


def done_assignment(title):
    assignments = load_assignments()
    remaining = remove_by_title(assignments, title)

    if len(remaining) == len(assignments):
        print(f"Error: no assignment titled '{title}'. Run 'list' to see the titles.")
        sys.exit(1)

    save_assignments(remaining)
    print(f"Marked done: {title}")

def sync_assignments():
    try:
        fetched = canvas.fetch_assignments()
    except canvas.CanvasError as error:
        print(f"Error: {error}")
        sys.exit(1)

    save_assignments(canvas.merge_synced(load_assignments(), fetched))
    print(f"Synced {len(fetched)} assignments from Canvas.")

def main():
    parser = argparse.ArgumentParser(description="Track your assignment deadlines.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="show upcoming assignments")
    list_parser.add_argument("--week", action="store_true", help="only show things due in the next 7 days")

    add_parser = subparsers.add_parser("add", help="add a new assignment")
    add_parser.add_argument("course", help='course code, like "PROG 101"')
    add_parser.add_argument("title", help="assignment name")
    add_parser.add_argument("due", help="due date as YYYY-MM-DD")

    done_parser = subparsers.add_parser("done", help="mark an assignment as done (removes it)")
    done_parser.add_argument("title", help="the assignment's title")
    
    subparsers.add_parser("sync", help="pull your upcoming assignments from Canvas")

    args = parser.parse_args()

    if args.command == "list":
        list_assignments(args.week)
    elif args.command == "add":
        add_assignment(args.course, args.title, args.due)
    elif args.command == "done":
        done_assignment(args.title)
    elif args.command == "sync":
        sync_assignments()


if __name__ == "__main__":
    main()