-- Schema for the Expense Tracker database.
--
-- Money is stored as an INTEGER number of cents ("amount_cents").
-- Storing money as a float (for example 12.30) is risky because binary
-- floating point cannot represent values such as 0.1 exactly, which leads to
-- totals that are off by tiny amounts. Integers are always exact.

CREATE TABLE IF NOT EXISTS expenses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    amount_cents  INTEGER NOT NULL,
    category      TEXT    NOT NULL,
    expense_date  TEXT    NOT NULL,           -- stored as YYYY-MM-DD
    description   TEXT    NOT NULL DEFAULT '',
    created_at    TEXT    NOT NULL            -- stored as ISO-8601 timestamp
);

-- Helpful for the "most recent expenses" query and for date based lookups.
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses (expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses (category);
