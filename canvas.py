import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

import re

import paths

BASE_URL = "https://learn.ontariotechu.ca"
TIMEZONE = ZoneInfo("America/Toronto")


class CanvasError(Exception):
    """A problem talking to Canvas, with a message safe to show the user."""


def get_all(path, token, params=None):
    """Fetch every page of results from a Canvas API endpoint."""
    url = BASE_URL + path
    headers = {"Authorization": f"Bearer {token}"}
    params = dict(params or {}, per_page=100)
    results = []
    while url:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 401:
            raise CanvasError("Canvas rejected your token. Check CANVAS_TOKEN in your .env file.")
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        params = None
    return results


def to_local_date(due_at):
    utc_time = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
    return utc_time.astimezone(TIMEZONE).date().isoformat()


def convert_assignment(canvas_assignment, course_code):
    if not canvas_assignment.get("due_at"):
        return None
    return {
        "course": course_code,
        "title": canvas_assignment["name"],
        "due": to_local_date(canvas_assignment["due_at"]),
        "canvas_id": canvas_assignment["id"],
    }


def merge_synced(existing, fetched):
    manual = [a for a in existing if "canvas_id" not in a]
    return manual + fetched

def drop_finished(fetched, done_ids):
    return [a for a in fetched if a["canvas_id"] not in done_ids]

def clean_course_name(raw):
    parts = [part.strip() for part in raw.split(" - ")]
    if len(parts) > 1 and parts[0].isdigit():
        parts = parts[1:]
    if len(parts) > 1 and re.fullmatch(r"\d+(\.\w+)*", parts[-1]):
        parts = parts[:-1]
    for part in parts:
        if re.fullmatch(r"[A-Z]{3,4}-\d{4}U", part):
            return part
    return " - ".join(parts)

def fetch_assignments():
    load_dotenv(paths.DATA_DIR / ".env")
    load_dotenv()
    token = os.getenv("CANVAS_TOKEN")
    if not token or token == "placeholder":
        raise CanvasError("No token found. Put CANVAS_TOKEN=your_token in your .env file.")

    fetched = []
    try:
        courses = get_all("/api/v1/courses", token, {"enrollment_state": "active"})
        for course in courses:
            if "course_code" not in course:
                continue
            assignments = get_all(
                f"/api/v1/courses/{course['id']}/assignments", token, {"bucket": "upcoming"}
            )
            for assignment in assignments:
                converted = convert_assignment(
                    assignment, clean_course_name(course["course_code"])
                )
                if converted:
                    fetched.append(converted)
    except requests.RequestException as error:
        raise CanvasError(f"Could not reach Canvas: {error}")
    return fetched