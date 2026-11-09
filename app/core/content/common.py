"""Shared pieces of the content API: the three error types (400/404/409), input validators and the audit actor.
Messages raised here are written by us and are safe to show; driver text never leaves the package."""

import re
from datetime import date

ACTOR = "owner"
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Invalid(Exception):
    """400: the request is malformed or a value is out of range."""


class NotFound(Exception):
    """404: an id in the path or body does not exist."""


class Conflict(Exception):
    """409: the request is valid but a rule, uniqueness or dependency forbids it."""


def text(body: dict, key: str, required: bool = False, maxlen: int = 200, allow_empty: bool = False):
    v = body.get(key)
    if v is None:
        if required:
            raise Invalid(f"{key} is required")
        return None
    if not isinstance(v, str):
        raise Invalid(f"{key} must be text")
    v = v.strip()
    if not v and not allow_empty:
        raise Invalid(f"{key} must be non-empty text")
    if len(v) > maxlen:
        raise Invalid(f"{key} is too long (max {maxlen})")
    return v


def iso_date(v, key: str = "planned_date"):
    """Strictly YYYY-MM-DD (date.fromisoformat alone also accepts 20261201 and week dates)."""
    if v is None:
        return None
    if not isinstance(v, str) or not _ISO_DATE.match(v):
        raise Invalid(f"{key} must be YYYY-MM-DD")
    try:
        return date.fromisoformat(v)
    except ValueError:
        raise Invalid(f"{key} must be YYYY-MM-DD") from None


def whole(v, key: str, lo: int = 1, hi: int = 10**9) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or not lo <= v <= hi:
        raise Invalid(f"{key} must be a whole number between {lo} and {hi}")
    return v


def only_keys(body: dict, allowed) -> None:
    unknown = set(body) - set(allowed)
    if unknown:
        raise Invalid("cannot change: " + ", ".join(sorted(unknown)))
