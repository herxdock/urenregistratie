import json
from datetime import date
from github import Github, GithubException
import streamlit as st


@st.cache_resource
def _client():
    return Github(st.secrets["github"]["token"])


@st.cache_resource
def _repo():
    return _client().get_repo(st.secrets["github"]["repo"])


def _month_path(d: date) -> str:
    return f"data/{d.year}-{d.month:02d}.json"


def load_month(d: date) -> dict:
    try:
        f = _repo().get_contents(_month_path(d))
        raw = f.decoded_content.decode("utf-8")
        return json.loads(raw) if raw.strip() else {}
    except GithubException as e:
        if e.status == 404:
            return {}
        raise


def save_month(d: date, data: dict, message: str) -> None:
    repo = _repo()
    path = _month_path(d)
    content = json.dumps(data, indent=2, ensure_ascii=False)
    try:
        existing = repo.get_contents(path)
        repo.update_file(path, message, content, existing.sha)
    except GithubException as e:
        if e.status == 404:
            repo.create_file(path, message, content)
        else:
            raise


def _migrate_entry(entry: dict, current_user: str) -> dict:
    """Zet oud formaat (top-level shifts/note) om naar users-formaat."""
    if "users" in entry:
        return entry
    old_shifts = entry.get("shifts", [])
    old_note = entry.get("note", "")
    users = {}
    if old_shifts or old_note:
        u = {}
        if old_shifts:
            u["shifts"] = old_shifts
        if old_note:
            u["note"] = old_note
        users[current_user] = u
    return {"users": users}


def load_day_full(d: date, user: str) -> dict:
    """Geeft {"shifts": [...], "note": "..."} voor één gebruiker."""
    entry = load_month(d).get(d.isoformat(), {})
    if "users" in entry:
        u = entry["users"].get(user, {})
        return {"shifts": u.get("shifts", []), "note": u.get("note", "")}
    # Oud formaat: toegewezen aan huidige user (migreert bij save)
    return {"shifts": entry.get("shifts", []), "note": entry.get("note", "")}


def load_day(d: date, user: str) -> list:
    return load_day_full(d, user)["shifts"]


def save_day(d: date, user: str, shifts: list = None, note: str = None) -> None:
    month = load_month(d)
    key = d.isoformat()
    entry = _migrate_entry(month.get(key, {}), user)

    users_data = entry.setdefault("users", {})
    u = users_data.setdefault(user, {})

    if shifts is not None:
        if shifts:
            u["shifts"] = shifts
        else:
            u.pop("shifts", None)

    if note is not None:
        if note.strip():
            u["note"] = note.strip()
        else:
            u.pop("note", None)

    if not u:
        users_data.pop(user, None)

    if users_data:
        month[key] = entry
    elif key in month:
        del month[key]

    save_month(d, month, f"Uren {key} [{user}]")


def delete_shift(d: date, user: str, shift_id: str) -> bool:
    month = load_month(d)
    key = d.isoformat()
    if key not in month:
        return False

    entry = _migrate_entry(month[key], user)
    users_data = entry.get("users", {})
    u = users_data.get(user, {})
    shifts = u.get("shifts", [])
    new_shifts = [s for s in shifts if s.get("id") != shift_id]

    if len(new_shifts) == len(shifts):
        return False

    if new_shifts:
        u["shifts"] = new_shifts
    else:
        u.pop("shifts", None)

    if not u:
        users_data.pop(user, None)
    if not users_data:
        month.pop(key, None)
    else:
        month[key] = entry

    save_month(d, month, f"Verwijder shift {shift_id} op {key} [{user}]")
    return True


def list_users_in_month(d: date) -> list[str]:
    """Geef alle gebruikersnamen die in deze maand data hebben."""
    month = load_month(d)
    names = set()
    for entry in month.values():
        if "users" in entry:
            names.update(entry["users"].keys())
    return sorted(names)
