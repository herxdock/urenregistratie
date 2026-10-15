import json
from github import GithubException
from src.github_store import _repo

SETTINGS_PATH = "data/settings.json"
DEFAULT_SETTINGS = {
    "shift_types": ["Standaard", "Verlof", "Ziekte", "Feestdag", "Opleiding"],
}


def load_settings() -> dict:
    try:
        f = _repo().get_contents(SETTINGS_PATH)
        data = json.loads(f.decoded_content.decode("utf-8"))
        if "shift_types" not in data or "Standaard" not in data["shift_types"]:
            data.setdefault("shift_types", []).insert(0, "Standaard")
        return data
    except GithubException as e:
        if e.status == 404:
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS
        raise


def save_settings(data: dict) -> None:
    repo = _repo()
    content = json.dumps(data, indent=2, ensure_ascii=False)
    try:
        existing = repo.get_contents(SETTINGS_PATH)
        repo.update_file(SETTINGS_PATH, "Update settings", content, existing.sha)
    except GithubException as e:
        if e.status == 404:
            repo.create_file(SETTINGS_PATH, "Create settings", content)
        else:
            raise
