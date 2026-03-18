import os

_INTERESTS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "interests.md")


def load_interests() -> str:
    """Load interests config file. Returns empty string if not found."""
    try:
        with open(_INTERESTS_PATH, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
