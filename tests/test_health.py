"""Tests for the /health endpoint."""

from expense_tracker.db import get_db


def test_health_returns_http_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_json(client):
    response = client.get("/health")
    assert response.headers["Content-Type"].startswith("application/json")


def test_health_reports_ok_status(client):
    payload = client.get("/health").get_json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"
    assert payload["service"] == "expense-tracker"


def test_health_works_after_adding_an_expense(client):
    client.post(
        "/expenses",
        data={
            "amount": "9.99",
            "category": "Transport",
            "date": "2024-05-01",
            "description": "Bus ticket",
        },
    )
    payload = client.get("/health").get_json()
    assert payload["status"] == "ok"


def test_health_uses_the_configured_database(app, client):
    """The health check must query the same database the app writes to."""
    with app.app_context():
        assert get_db().execute("SELECT 1").fetchone()[0] == 1
    assert client.get("/health").status_code == 200
