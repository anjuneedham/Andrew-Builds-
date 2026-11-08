"""Every content request runs inside ONE transaction as the content_app role.

SET LOCAL (not SET) on purpose: it ends with the transaction, so it can never leak to another client when the database
sits behind a transaction-pooling proxy (Neon's pooled URL). content_app can touch only the content tables, append to the
audit log and read a prospect's id/name/business/stage; it has no access to owner_credentials or sessions."""

from contextlib import contextmanager

from core.content.meta import ROLE

RULE_PREFIX = "CONTENT_RULE:"


@contextmanager
def content_session(conn):
    with conn.transaction():
        conn.execute(f"SET LOCAL ROLE {ROLE}")
        yield conn


def rule_message(exc) -> str | None:
    """The human message of a business-rule violation raised by our own triggers, else None.
    Anything else (constraint names, driver text) must never reach the client."""
    diag = getattr(exc, "diag", None)
    msg = getattr(diag, "message_primary", None) or ""
    return msg[len(RULE_PREFIX):].strip() if msg.startswith(RULE_PREFIX) else None
