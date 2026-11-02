# Assignment Tracker

A command-line tool that pulls upcoming deadlines from Canvas and shows what's due, sorted by date. Built in Python as a first portfolio project.

## Features

- `list` shows upcoming assignments sorted by due date, with days remaining
- `list --week` shows only what's due in the next 7 days
- `add` creates your own entries for things that aren't in Canvas
- `done` marks an assignment finished, and it stays gone after the next sync
- `sync` pulls your upcoming assignments from Canvas using its API
- Tested with `pytest`, with clear error messages instead of crashes

## Example

```
$ tracker list --week
Upcoming assignments
--------------------
PROG-1000U: Lab 3 report - due 2026-11-05 (3 days left)
MATH-1010U: Problem set 4 - due 2026-11-06 (4 days left)
```

## Setup

You'll need Python 3.9 or newer.

```
git clone https://github.com/misbahu28/assignment-tracker.git
cd assignment-tracker
python -m pip install -e .
```

This installs the `tracker` command.

### Connecting to Canvas

1. In Canvas, go to Account > Settings > Approved Integrations and create a new access token.
2. Create a file named `.env` in the tool's data folder (`~/.assignment-tracker/`) containing:

```
CANVAS_TOKEN=your_token_here
```

3. Edit `BASE_URL` in `canvas.py` if your school uses a different Canvas address (it's currently set to Ontario Tech's).

Your data and token stay on your computer and are never part of the repository.

## Usage

```
tracker sync
tracker list
tracker list --week
tracker add "PROG-1000U" "Lab 4" 2026-11-20
tracker done "Lab 4"
tracker --help
```

## Running the tests

```
python -m pytest
```

## How it works

- `tracker.py` handles the command-line interface and local storage (a JSON file)
- `canvas.py` talks to the Canvas REST API, handles pagination, and converts UTC deadlines to local dates
- Assignments you add by hand are kept separate from synced ones, so a sync never overwrites them
- Finished Canvas assignments are remembered by ID so they don't reappear

## Ideas for next steps

- Make it installable with `pip install` so `tracker` works from any folder
- Support more than one Canvas site
- Color-code assignments by urgency