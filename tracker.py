import json
from datetime import date


def get_due_date(assignment):
    return assignment["due"]


with open("assignments.json") as file:
    assignments = json.load(file)

assignments = sorted(assignments, key=get_due_date)

today = date.today()

print("Upcoming assignments")
print("--------------------")
for assignment in assignments:
    due = date.fromisoformat(assignment["due"])
    days_left = (due - today).days
    print(f"{assignment['course']}: {assignment['title']} - due {assignment['due']} ({days_left} days left)")