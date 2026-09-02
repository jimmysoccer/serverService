import json
import os
from datetime import datetime, date
from pathlib import Path

import requests
from dotenv import load_dotenv
from icalendar import Calendar

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from fastapi import HTTPException

from .canvas_router import canvas_router


load_dotenv()

CANVAS_ICAL_URL = os.getenv("CANVAS_ICAL_URL")

SCOPES = ["https://www.googleapis.com/auth/tasks"]

TASK_LIST_NAME = "Canvas Assignments"
MAX_TASK_TITLE_LENGTH = 1024
MAX_TASK_NOTES_LENGTH = 8192

BACKEND_DIR = Path(__file__).resolve().parents[3]
TOKEN_PATH = Path(os.getenv("GOOGLE_TOKEN_PATH", BACKEND_DIR / "token.json"))
CREDENTIALS_PATH = Path(
    os.getenv("GOOGLE_CREDENTIALS_PATH", BACKEND_DIR / "credentials.json")
)


class GoogleAuthorizationRequired(RuntimeError):
    """Raised when the stored Google grant is missing, expired, or revoked."""


# --------------------------------------------------
# Google authentication
# --------------------------------------------------


def _credentials_from_environment():
    token_json = os.getenv("GOOGLE_TOKEN_JSON")
    if not token_json:
        return None

    try:
        return Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    except (TypeError, ValueError, KeyError) as exc:
        raise GoogleAuthorizationRequired(
            "GOOGLE_TOKEN_JSON is not a valid authorized-user token."
        ) from exc


def _save_credentials(creds, *, force=False):
    # An environment-provided refresh token is deliberately not written to the
    # instance filesystem. It remains usable even when its access token expires.
    if os.getenv("GOOGLE_TOKEN_JSON") and not force:
        return

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")


def get_google_service():
    creds = _credentials_from_environment()

    if creds is None and TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as exc:
                raise GoogleAuthorizationRequired(
                    "Google authorization expired or was revoked. Run the local "
                    "authorization command again and replace GOOGLE_TOKEN_JSON "
                    "in the deployed service."
                ) from exc
        else:
            raise GoogleAuthorizationRequired(
                "Google Tasks is not authorized. Run the local authorization command first."
            )

        _save_credentials(creds)

    return build("tasks", "v1", credentials=creds)


def authorize_google():
    """Perform the interactive desktop flow; never call this from a web request."""
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"Missing OAuth client file: {CREDENTIALS_PATH}")

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )
    _save_credentials(creds, force=True)
    return creds


# --------------------------------------------------
# Find/create Canvas task list
# --------------------------------------------------


def get_canvas_task_list(service):
    results = service.tasklists().list().execute()

    for task_list in results.get("items", []):
        if task_list["title"] == TASK_LIST_NAME:
            return task_list["id"]

    new_list = service.tasklists().insert(body={"title": TASK_LIST_NAME}).execute()

    return new_list["id"]


# --------------------------------------------------
# Download Canvas calendar
# --------------------------------------------------


def get_canvas_events():
    response = requests.get(CANVAS_ICAL_URL, timeout=30)

    response.raise_for_status()

    calendar = Calendar.from_ical(response.content)

    events = []

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue

        title = str(component.get("SUMMARY", "Canvas Assignment"))
        uid = str(component.get("UID", ""))
        description = str(component.get("DESCRIPTION", ""))

        dtstart = component.get("DTSTART")

        if not dtstart:
            continue

        due = dtstart.dt

        events.append(
            {"title": title, "uid": uid, "description": description, "due": due}
        )

    return events


# --------------------------------------------------
# Google Tasks helpers
# --------------------------------------------------


def get_existing_tasks(service, task_list_id):
    tasks = []
    page_token = None

    while True:
        result = (
            service.tasks()
            .list(
                tasklist=task_list_id,
                showCompleted=True,
                showHidden=True,
                maxResults=100,
                pageToken=page_token,
            )
            .execute()
        )

        tasks.extend(result.get("items", []))

        page_token = result.get("nextPageToken")

        if not page_token:
            break

    return tasks


def canvas_uid_from_task(task):
    notes = task.get("notes", "")

    marker = "CANVAS_UID:"

    for line in notes.splitlines():
        if line.startswith(marker):
            return line[len(marker) :].strip()

    return None


def google_due_date(canvas_due):
    if isinstance(canvas_due, datetime):
        due_date = canvas_due.date()
    elif isinstance(canvas_due, date):
        due_date = canvas_due
    else:
        return None

    # Google Tasks stores only the date portion and can reject otherwise valid
    # RFC 3339 variants. Use its canonical midnight-UTC representation.
    return f"{due_date.isoformat()}T00:00:00.000Z"


def readable_due_time(canvas_due):
    if isinstance(canvas_due, datetime):
        return canvas_due.strftime("%B %d, %Y at %I:%M %p")

    return canvas_due.strftime("%B %d, %Y")


def google_task_notes(event, canvas_due):
    prefix = (
        "Canvas assignment\n\n"
        f"Original Canvas due: {readable_due_time(canvas_due)}\n\n"
    )
    suffix = f"\n\nCANVAS_UID:{event['uid']}"
    available_description_length = max(
        0, MAX_TASK_NOTES_LENGTH - len(prefix) - len(suffix)
    )
    description = event["description"][:available_description_length]
    return f"{prefix}{description}{suffix}"


# --------------------------------------------------
# Sync
# --------------------------------------------------


def sync():
    if not CANVAS_ICAL_URL:
        raise RuntimeError("CANVAS_ICAL_URL is missing from .env")

    print("Connecting to Google Tasks...")

    service = get_google_service()

    task_list_id = get_canvas_task_list(service)

    print("Downloading Canvas calendar...")

    canvas_events = get_canvas_events()

    print(f"Found {len(canvas_events)} Canvas events.")

    existing_tasks = get_existing_tasks(service, task_list_id)

    existing_by_uid = {}

    for task in existing_tasks:
        uid = canvas_uid_from_task(task)

        if uid:
            existing_by_uid[uid] = task

    created = 0
    updated = 0
    skipped = 0

    today = date.today()

    for event in canvas_events:

        canvas_due = event["due"]

        if isinstance(canvas_due, datetime):
            due_date = canvas_due.date()
        else:
            due_date = canvas_due

        # Ignore old assignments
        if due_date < today:
            skipped += 1
            continue

        uid = event["uid"]

        notes = google_task_notes(event, canvas_due)

        body = {
            "title": event["title"][:MAX_TASK_TITLE_LENGTH],
            "notes": notes,
            "due": google_due_date(canvas_due),
        }

        existing = existing_by_uid.get(uid)

        if existing:

            # Do NOT reopen assignments you've completed.
            if existing.get("status") == "completed":
                skipped += 1
                continue

            service.tasks().patch(
                tasklist=task_list_id, task=existing["id"], body=body
            ).execute()

            print(f"Updated: {event['title']}")

            updated += 1

        else:

            service.tasks().insert(tasklist=task_list_id, body=body).execute()

            print(f"Created: {event['title']}")

            created += 1

    print()
    print("Sync complete!")
    print(f"Created: {created}")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")


@canvas_router.get("/sync")
async def canvas_sync():
    try:
        sync()
        return {"message": "Sync complete!"}
    except GoogleAuthorizationRequired as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Canvas sync failed: {e}") from e
