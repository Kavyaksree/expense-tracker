"""Input validation helpers.

Each function returns a tuple of ``(value, error_message)``:
  * ``value``  is the cleaned value when the input is valid, otherwise ``None``.
  * ``error_message`` is ``None`` when the input is valid, otherwise a short
    sentence that is safe to show to the user.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
import re

MAX_AMOUNT_CENTS = 100_000_000  # 1,000,000.00
MAX_DESCRIPTION_LENGTH = 200

# A plain decimal number such as "12", "12.5" or "-3.25".
# Anything else (letters, scientific notation like "1e3", "1_000") is rejected
# so the user gets a clear message instead of a surprising value.
NUMBER_PATTERN = re.compile(r"^[+-]?\d+(\.\d+)?$")


def parse_amount(raw_value):
    """Convert a text amount such as "12.50" into an integer number of cents.

    Returns ``(cents, None)`` when the value is valid and
    ``(None, message)`` when it is not.
    """
    text = (raw_value or "").strip()

    if not text:
        return None, "Amount is required."

    if not NUMBER_PATTERN.match(text):
        return None, "Amount must be a number, for example 12.50."

    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError, ArithmeticError):
        return None, "Amount must be a number, for example 12.50."

    # Reject NaN and Infinity, which Decimal accepts but make no sense here.
    if not amount.is_finite():
        return None, "Amount must be a real number, for example 12.50."

    if amount <= 0:
        return None, "Amount must be greater than zero."

    # More than two decimal places means sub-cent precision. Rejecting it is
    # clearer than silently rounding it and losing money.
    if amount.as_tuple().exponent < -2:
        return None, "Amount can have at most 2 decimal places."

    cents = int(amount * 100)
    if cents > MAX_AMOUNT_CENTS:
        return None, "Amount is too large (maximum 1,000,000.00)."

    return cents, None


def parse_expense_date(raw_value):
    """Validate a date string and return it in YYYY-MM-DD form."""
    text = (raw_value or "").strip()

    if not text:
        return None, "Date is required."

    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        return None, "Date must be a valid date in YYYY-MM-DD format."

    if parsed > date.today():
        return None, "Date cannot be in the future."

    return parsed.isoformat(), None


def parse_category(raw_value, allowed_categories):
    """Check that the category is one of the configured categories."""
    text = (raw_value or "").strip()

    if not text:
        return None, "Category is required."

    if text not in allowed_categories:
        return None, "Category must be one of: " + ", ".join(allowed_categories) + "."

    return text, None


def parse_description(raw_value):
    """Clean the description: strip whitespace and limit its length."""
    text = (raw_value or "").strip()
    return text[:MAX_DESCRIPTION_LENGTH], None


def format_cents(cents, symbol="$"):
    """Render integer cents as a readable string such as "$12.50"."""
    if cents is None:
        cents = 0
    sign = "-" if cents < 0 else ""
    whole, remainder = divmod(abs(int(cents)), 100)
    return f"{sign}{symbol}{whole}.{remainder:02d}"
