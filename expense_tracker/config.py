"""Application configuration.

Every deployment-specific value lives in this file and can be overridden with
an environment variable. That way the same code runs on a laptop, inside
Jenkins, and on an Azure virtual machine without any edits.

Environment variables used:
    EXPENSE_DB_PATH         Full path to the SQLite database file.
    EXPENSE_SECRET_KEY      Flask secret key (used to sign flash messages).
    EXPENSE_CURRENCY_SYMBOL Symbol shown in front of amounts.
"""

import os
from pathlib import Path

# BASE_DIR is the project root (the parent folder of this package).
BASE_DIR = Path(__file__).resolve().parent.parent

# Categories are fixed in configuration so that the "add expense" form and the
# category summary can never disagree with each other.
DEFAULT_CATEGORIES = (
    "Food",
    "Transport",
    "Housing",
    "Utilities",
    "Health",
    "Entertainment",
    "Other",
)


class Config:
    """Default settings for the Expense Tracker."""

    # Flask uses this key to sign session data (flash messages).
    # The default is fine for local development only. Set EXPENSE_SECRET_KEY
    # to a random value in any shared or production environment.
    SECRET_KEY = os.environ.get("EXPENSE_SECRET_KEY", "dev-only-change-me")

    # Explicit, persistent database file. The data survives restarts because
    # it is written to disk in the instance folder, not in memory.
    DATABASE_PATH = os.environ.get(
        "EXPENSE_DB_PATH", str(BASE_DIR / "instance" / "expenses.db")
    )

    CURRENCY_SYMBOL = os.environ.get("EXPENSE_CURRENCY_SYMBOL", "$")

    CATEGORIES = DEFAULT_CATEGORIES

    # Guards against absurd values that could overflow the column.
    MAX_AMOUNT_CENTS = 100_000_000  # 1,000,000.00
