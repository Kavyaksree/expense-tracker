"""Web routes for the Expense Tracker.

Routes:
    GET  /                              - the single page application
    POST /expenses                      - add an expense
    POST /expenses/<id>/delete          - delete an expense
    GET  /health                        - health check used by monitoring
"""

import sqlite3

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from .db import get_db, utc_now_iso
from .validation import (
    format_cents,
    parse_amount,
    parse_category,
    parse_description,
    parse_expense_date,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Show the add form, all expenses, the total and the category summary."""
    database = get_db()

    expenses = database.execute(
        "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
    ).fetchall()

    total_cents = database.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS total FROM expenses"
    ).fetchone()["total"]

    summary = database.execute(
        """
        SELECT category, SUM(amount_cents) AS total, COUNT(*) AS count
        FROM expenses
        GROUP BY category
        ORDER BY total DESC, category ASC
        """
    ).fetchall()

    return render_template(
        "index.html",
        expenses=expenses,
        total_cents=total_cents,
        summary=summary,
        categories=current_app.config["CATEGORIES"],
        currency=current_app.config["CURRENCY_SYMBOL"],
    )


@main_bp.route("/expenses", methods=["POST"])
def add_expense():
    """Validate the submitted form and store the expense."""
    amount_cents, amount_error = parse_amount(request.form.get("amount"))
    expense_date, date_error = parse_expense_date(request.form.get("date"))
    category, category_error = parse_category(
        request.form.get("category"), current_app.config["CATEGORIES"]
    )
    description, _ = parse_description(request.form.get("description"))

    errors = [message for message in (amount_error, date_error, category_error) if message]
    if errors:
        for message in errors:
            flash(message, "error")
        return redirect(url_for("main.index"))

    database = get_db()
    database.execute(
        """
        INSERT INTO expenses (amount_cents, category, expense_date, description, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (amount_cents, category, expense_date, description, utc_now_iso()),
    )
    database.commit()

    flash(
        f"Added {format_cents(amount_cents, current_app.config['CURRENCY_SYMBOL'])} "
        f"to {category}.",
        "success",
    )
    return redirect(url_for("main.index"))


@main_bp.route("/expenses/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    """Delete one expense and return to the list."""
    database = get_db()
    cursor = database.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    database.commit()

    if cursor.rowcount:
        flash("Expense deleted.", "success")
    else:
        flash("That expense no longer exists.", "error")

    return redirect(url_for("main.index"))


@main_bp.route("/health")
def health():
    """Health check used by monitoring tools and by the CI/CD pipeline.

    Returns HTTP 200 and a JSON body when the application and the database
    are both working, and HTTP 503 when the database cannot be reached.
    """
    database_status = "ok"
    status_code = 200

    try:
        get_db().execute("SELECT 1").fetchone()
    except sqlite3.Error:
        database_status = "unavailable"
        status_code = 503

    return (
        jsonify(
            {
                "status": "ok" if status_code == 200 else "degraded",
                "database": database_status,
                "service": "expense-tracker",
            }
        ),
        status_code,
    )
