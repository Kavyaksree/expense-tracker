"""Shared pytest fixtures.

Every test gets its own application and its own temporary database file, so
tests never touch the real data in ``instance/expenses.db`` and can run in
any order without interfering with each other.
"""

import pytest

from expense_tracker import create_app
from expense_tracker.db import get_db

# A date in the past, so the "date cannot be in the future" rule never
# interferes with the other tests.
SAMPLE_DATE = "2024-05-01"


@pytest.fixture()
def app(tmp_path):
    """An application configured to use a temporary database file."""
    database_path = tmp_path / "test_expenses.db"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": str(database_path),
        }
    )
    yield application


@pytest.fixture()
def client(app):
    """A test client that can send requests to the application."""
    return app.test_client()


@pytest.fixture()
def database(app):
    """The SQLite connection, with an active application context."""
    with app.app_context():
        yield get_db()


def add_expense(client, amount="12.50", category="Food", date=SAMPLE_DATE, description="Lunch"):
    """Helper: submit the add-expense form and return the response."""
    return client.post(
        "/expenses",
        data={
            "amount": amount,
            "category": category,
            "date": date,
            "description": description,
        },
        follow_redirects=False,
    )


def row_count(database):
    """Helper: number of expenses currently stored."""
    return database.execute("SELECT COUNT(*) AS c FROM expenses").fetchone()["c"]


def fetch_expenses(database):
    """Helper: all stored expenses, newest first."""
    return database.execute(
        "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
    ).fetchall()
