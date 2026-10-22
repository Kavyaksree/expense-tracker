"""SQLite database helpers.

The pattern used here is the standard Flask "one connection per request"
pattern:
  * ``get_db()``  returns the connection for the current request (creating it
    on first use) and stores it on Flask's ``g`` object.
  * ``close_db()``  is registered as a teardown handler, so the connection is
    always closed when the request ends, even if an error occurred.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app, g

SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


def get_db():
    """Return the SQLite connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # Rows behave like dictionaries, so we can read them by column name.
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    """Close the connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create the database file and the table if they do not exist yet.

    This runs once when the application starts, so a fresh deployment is
    immediately usable without any manual SQL steps.
    """
    database_path = Path(app.config["DATABASE_PATH"])
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()


def utc_now_iso():
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
