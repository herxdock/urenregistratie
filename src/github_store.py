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


def load_day(d: date) -> list:
    return load_month(d).get(d.isoformat(), {}).get("shifts", [])


def save_day(d: date, shifts: list) -> None:
    month = load_month(d)
    key = d.isoformat()
    if shifts:
        month[key] = {"shifts": shifts}
    elif key in month:
        del month[key]
    save_month(d, month, f"Uren {key}")


def delete_shift(d: date, shift_id: str) -> bool:
    month = load_month(d)
    key = d.isoformat()
    if key not in month:
        return False

    shifts = month[key].get("shifts", [])
    new_shifts = [s for s in shifts if s.get("id") != shift_id]

    if len(new_shifts) == len(shifts):
        return False

    if new_shifts:
        month[key] = {"shifts": new_shifts}
    else:
        del month[key]

    save_month(d, month, f"Verwijder shift {shift_id} op {key}")
    return True
