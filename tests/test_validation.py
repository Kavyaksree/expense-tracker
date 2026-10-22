"""Tests for input validation and safe handling of user input."""

from datetime import date, timedelta

from conftest import add_expense, row_count

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


def page_text(client):
    return client.get("/").data.decode("utf-8")


# ---------------------------------------------------------------- amounts


def test_amount_is_required(client, database):
    add_expense(client, amount="")
    assert "Amount is required." in page_text(client)
    assert row_count(database) == 0


def test_zero_amount_is_rejected(client, database):
    add_expense(client, amount="0")
    assert "Amount must be greater than zero." in page_text(client)
    assert row_count(database) == 0


def test_negative_amount_is_rejected(client, database):
    add_expense(client, amount="-5.00")
    assert "Amount must be greater than zero." in page_text(client)
    assert row_count(database) == 0


def test_non_numeric_amount_is_rejected(client, database):
    add_expense(client, amount="abc")
    assert "Amount must be a number" in page_text(client)
    assert row_count(database) == 0


def test_scientific_notation_amount_is_rejected(client, database):
    """'1e3' is a valid Python number but not a sensible user input."""
    add_expense(client, amount="1e3")
    assert "Amount must be a number" in page_text(client)
    assert row_count(database) == 0


def test_amount_with_more_than_two_decimals_is_rejected(client, database):
    add_expense(client, amount="10.999")
    assert "at most 2 decimal places" in page_text(client)
    assert row_count(database) == 0


def test_very_large_amount_is_rejected(client, database):
    add_expense(client, amount="99999999")
    assert "Amount is too large" in page_text(client)
    assert row_count(database) == 0


def test_smallest_positive_amount_is_accepted(client, database):
    add_expense(client, amount="0.01")
    assert row_count(database) == 1


# ------------------------------------------------------------------ dates


def test_date_is_required(client, database):
    add_expense(client, date="")
    assert "Date is required." in page_text(client)
    assert row_count(database) == 0


def test_invalid_date_format_is_rejected(client, database):
    add_expense(client, date="01-05-2024")
    assert "valid date in YYYY-MM-DD format" in page_text(client)
    assert row_count(database) == 0


def test_future_date_is_rejected(client, database):
    add_expense(client, date=TOMORROW)
    assert "Date cannot be in the future." in page_text(client)
    assert row_count(database) == 0


# -------------------------------------------------------------- categories


def test_category_is_required(client, database):
    add_expense(client, category="")
    assert "Category is required." in page_text(client)
    assert row_count(database) == 0


def test_unknown_category_is_rejected(client, database):
    add_expense(client, category="Crypto")
    assert "Category must be one of" in page_text(client)
    assert row_count(database) == 0


# ----------------------------------------------------------- description


def test_description_is_optional(client, database):
    """An empty description is allowed and is stored as an empty string."""
    add_expense(client, description="")

    from expense_tracker.db import get_db

    with client.application.app_context():
        stored = get_db().execute("SELECT description FROM expenses").fetchone()["description"]

    assert row_count(database) == 1
    assert stored == ""


def test_long_description_is_truncated_to_200_characters(client, database):
    add_expense(client, description="x" * 250)

    from expense_tracker.db import get_db

    with client.application.app_context():
        stored = get_db().execute("SELECT description FROM expenses").fetchone()["description"]

    assert len(stored) == 200


# ------------------------------------------------------------ safe output


def test_html_in_the_description_is_escaped(client):
    add_expense(client, description="<script>alert('xss')</script>")
    html = page_text(client)
    assert "<script>alert('xss')</script>" not in html
    assert "&lt;script&gt;" in html


def test_sql_injection_in_the_description_is_stored_as_plain_text(client, database):
    payload = "Robert'); DROP TABLE expenses;--"
    add_expense(client, description=payload)

    from expense_tracker.db import get_db

    with client.application.app_context():
        stored = get_db().execute("SELECT description FROM expenses").fetchone()["description"]
        still_there = get_db().execute(
            "SELECT COUNT(*) AS c FROM sqlite_master WHERE type='table' AND name='expenses'"
        ).fetchone()["c"]

    assert stored == payload
    assert still_there == 1


def test_database_is_not_affected_by_an_invalid_expense(client, database):
    """A rejected submission must leave the stored data untouched."""
    add_expense(client, amount="10.00", description="Valid one")
    add_expense(client, amount="-1", description="Invalid one")

    assert row_count(database) == 1
