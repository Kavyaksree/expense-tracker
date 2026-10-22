"""Tests for adding, listing and deleting expenses, totals and summaries."""

from conftest import SAMPLE_DATE, add_expense, fetch_expenses, row_count


# --------------------------------------------------------------------- add


def test_add_expense_redirects_back_to_the_list(client):
    response = add_expense(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_add_expense_stores_the_row(client, database):
    add_expense(client, amount="12.50", category="Food", description="Lunch")

    expenses = fetch_expenses(database)
    assert row_count(database) == 1

    expense = expenses[0]
    assert expense["amount_cents"] == 1250  # stored as exact integer cents
    assert expense["category"] == "Food"
    assert expense["expense_date"] == SAMPLE_DATE
    assert expense["description"] == "Lunch"
    assert expense["created_at"]


def test_add_expense_shows_a_success_message(client):
    add_expense(client, amount="12.50")
    html = client.get("/").data.decode("utf-8")
    assert "Added" in html
    assert "$12.50" in html


def test_add_expense_accepts_a_whole_number_amount(client, database):
    add_expense(client, amount="8")
    assert fetch_expenses(database)[0]["amount_cents"] == 800


# ------------------------------------------------------------------- list


def test_list_page_shows_stored_expenses(client):
    add_expense(client, amount="10.00", category="Food", description="Groceries")
    add_expense(client, amount="20.00", category="Transport", description="Bus pass")

    html = client.get("/").data.decode("utf-8")
    assert "Groceries" in html
    assert "Bus pass" in html
    assert "Food" in html
    assert "Transport" in html


def test_list_page_shows_a_message_when_there_are_no_expenses(client):
    html = client.get("/").data.decode("utf-8")
    assert "No expenses yet" in html


# ----------------------------------------------------------------- delete


def test_delete_expense_removes_the_row(client, database):
    add_expense(client, amount="10.00", description="Groceries")
    expense_id = fetch_expenses(database)[0]["id"]

    response = client.post(f"/expenses/{expense_id}/delete")
    assert response.status_code == 302
    assert row_count(database) == 0


def test_delete_expense_keeps_the_other_rows(client, database):
    add_expense(client, amount="10.00", description="Keep me")
    add_expense(client, amount="20.00", description="Delete me")

    expenses = fetch_expenses(database)
    delete_id = next(row["id"] for row in expenses if row["description"] == "Delete me")

    client.post(f"/expenses/{delete_id}/delete")

    remaining = fetch_expenses(database)
    assert row_count(database) == 1
    assert remaining[0]["description"] == "Keep me"


def test_delete_unknown_expense_is_handled_gracefully(client, database):
    response = client.post("/expenses/9999/delete")
    assert response.status_code == 302
    assert row_count(database) == 0
    html = client.get("/").data.decode("utf-8")
    assert "no longer exists" in html


def test_delete_expense_rejects_get_requests(client, database):
    """Deleting is a state change, so it must not be done with a GET."""
    add_expense(client)
    response = client.get("/expenses/1/delete")
    assert response.status_code == 405
    assert row_count(database) == 1


# ------------------------------------------------------------------ total


def test_total_spending_is_the_sum_of_all_expenses(client):
    add_expense(client, amount="10.50")
    add_expense(client, amount="4.25")
    add_expense(client, amount="0.75")

    html = client.get("/").data.decode("utf-8")
    assert "$15.50" in html


def test_total_spending_is_zero_when_there_are_no_expenses(client):
    html = client.get("/").data.decode("utf-8")
    assert "$0.00" in html


def test_total_spending_avoids_floating_point_rounding_errors(client, database):
    """0.10 + 0.20 must be exactly 0.30, not 0.30000000000000004."""
    add_expense(client, amount="0.10")
    add_expense(client, amount="0.20")

    html = client.get("/").data.decode("utf-8")
    assert "$0.30" in html
    assert "$0.300000" not in html


# ---------------------------------------------------------------- summary


def test_category_summary_groups_and_sorts_by_total(client):
    add_expense(client, amount="10.00", category="Food")
    add_expense(client, amount="5.00", category="Food")
    add_expense(client, amount="20.00", category="Transport")

    html = client.get("/").data.decode("utf-8")
    assert "$15.00" in html  # Food: 10.00 + 5.00
    assert "$20.00" in html  # Transport


def test_category_summary_is_computed_correctly_in_the_database(client, database):
    add_expense(client, amount="10.00", category="Food")
    add_expense(client, amount="5.00", category="Food")
    add_expense(client, amount="20.00", category="Transport")

    summary = database.execute(
        """
        SELECT category, SUM(amount_cents) AS total, COUNT(*) AS count
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
        """
    ).fetchall()

    assert len(summary) == 2
    assert summary[0]["category"] == "Transport"
    assert summary[0]["total"] == 2000
    assert summary[0]["count"] == 1
    assert summary[1]["category"] == "Food"
    assert summary[1]["total"] == 1500
    assert summary[1]["count"] == 2


# ------------------------------------------------------------ persistence


def test_database_file_is_created_at_the_configured_path(app):
    from pathlib import Path

    assert Path(app.config["DATABASE_PATH"]).exists()


def test_expenses_survive_a_new_application_instance(app, client, tmp_path):
    """Data must be on disk, so a restart does not lose it."""
    add_expense(client, amount="33.00", description="Persisted")

    from expense_tracker import create_app

    restarted = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_PATH": app.config["DATABASE_PATH"],
        }
    )
    with restarted.app_context():
        from expense_tracker.db import get_db

        rows = get_db().execute("SELECT * FROM expenses").fetchall()

    assert len(rows) == 1
    assert rows[0]["description"] == "Persisted"
    assert rows[0]["amount_cents"] == 3300
