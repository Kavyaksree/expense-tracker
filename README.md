# Expense Tracker

A small web application for recording expenses, written in **Python 3.11 + Flask + SQLite**
with a Bootstrap 5.3 interface.

This repository is the application part of a larger DevOps project. Later phases add
Terraform (Azure infrastructure) and a Jenkins pipeline (CI/CD). **Phase 1 is complete,
so nothing else is configured yet.**

---

## 1. Features

| # | Feature | Where it lives |
|---|---------|-----------------|
| 1 | Add an expense (amount, category, date, description) | `POST /expenses` |
| 2 | List all saved expenses | `GET /` |
| 3 | Delete an expense | `POST /expenses/<id>/delete` |
| 4 | Total spending | `GET /` (total card) |
| 5 | Category-wise summary | `GET /` (summary table) |
| 6 | Persistent storage in SQLite | `instance/expenses.db` |
| 7 | Health endpoint (JSON + HTTP 200) | `GET /health` |
| 8 | Input validation, readable errors, responsive UI | `expense_tracker/validation.py` |

### Why money is stored as integer cents

Amounts are stored in a column called `amount_cents` (`INTEGER`) and never as a
floating point number. A float cannot represent `0.10` exactly, so adding
`0.10 + 0.20` gives `0.30000000000000004` and totals drift over time. Integers are
always exact, so the totals stay correct. The interface converts between the two
(`$12.50` on screen, `1250` in the database).

---

## 2. Requirements

Check what you already have (all commands are run from the project folder):

```powershell
python --version      # must show Python 3.11.x
git --version
```

If Python 3.11 is not installed, download it from <https://www.python.org/downloads/>
and tick **"Add Python to PATH"** during installation.

---

## 3. Setup on Windows (PowerShell)

Open PowerShell in the project folder (`C:\Users\H P\Music\devops`) and run:

```powershell
# 1. Create the virtual environment (an isolated copy of Python for this project)
python -m venv .venv

# 2. Activate it
.\.venv\Scripts\Activate.ps1
```

> If PowerShell refuses to activate the script, run this once in the same window:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> and confirm with `Y`.

```powershell
# 3. Install the dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Confirm the versions that got installed
pip list
```

Expected versions: `Flask 3.0.3`, `gunicorn 22.0.0`, `pytest 8.2.0`.

> `gunicorn` is a Linux production server. It installs on Windows but is only used
> later, on the Azure VM, in the Jenkins deploy stage.

---

## 4. Run the application

```powershell
# Make sure the virtual environment is active
.\.venv\Scripts\Activate.ps1

python run.py
```

Then open <http://127.0.0.1:5000> in your browser.

The first start creates the database file `instance\expenses.db` automatically.
Stop the server with `Ctrl + C`.

---

## 5. Run the tests

```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

Useful variants:

```powershell
pytest -v tests/test_health.py      # only the health endpoint tests
pytest -v -k validation             # only the validation tests
pytest -v --tb=short                # shorter traceback when a test fails
```

The tests never touch your real data: each test gets its own temporary database
file (see `tests/conftest.py`).

---

## 6. Configuration

Nothing deployment-specific is hardcoded. All settings live in
`expense_tracker/config.py` and can be changed with environment variables.

| Variable | Default | Purpose |
|----------|---------|---------|
| `EXPENSE_DB_PATH` | `<project>\instance\expenses.db` | Full path to the SQLite file |
| `EXPENSE_SECRET_KEY` | `dev-only-change-me` | Signs flash messages. **Change this outside local development.** |
| `EXPENSE_CURRENCY_SYMBOL` | `$` | Symbol shown in front of amounts |

Example (PowerShell):

```powershell
$env:EXPENSE_DB_PATH = "C:\data\expenses.db"
$env:EXPENSE_SECRET_KEY = "some-long-random-string"
python run.py
```

The list of allowed categories is also configuration (`CATEGORIES` in
`expense_tracker/config.py`). Adding a category there automatically adds it to
the form and to the summary.

---

## 7. Project structure

```
devops/
|-- expense_tracker/
|   |-- __init__.py      create_app(): builds the Flask application
|   |-- config.py        settings, overridable with environment variables
|   |-- db.py            SQLite connection handling
|   |-- schema.sql       table definition (amount stored as integer cents)
|   |-- validation.py    amount/date/category checks, money formatting
|   `-- routes.py        the four routes
|-- templates/
|   |-- base.html        layout, navbar, flash messages
|   `-- index.html       form, totals, summary and expense list
|-- static/css/style.css small additions on top of Bootstrap
|-- tests/
|   |-- conftest.py      fixtures (temporary database per test)
|   |-- test_health.py
|   |-- test_expenses.py
|   `-- test_validation.py
|-- instance/            the SQLite database lives here (ignored by Git)
|-- requirements.txt
|-- run.py               start the app locally
`-- .gitignore
```

---

## 8. Troubleshooting

| Problem | Cause and fix |
|---------|---------------|
| `python` is not recognised | Python is not on PATH. Reinstall with "Add Python to PATH", or reopen the terminal. |
| `Activate.ps1 cannot be loaded... running scripts is disabled` | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` and answer `Y`. |
| `ModuleNotFoundError: No module named 'flask'` | The virtual environment is not active. Activate it and run `pip install -r requirements.txt`. |
| `Address already in use` / port 5000 busy | Another program uses port 5000. Stop it, or change the port in `run.py`. |
| The page shows "No expenses yet" after adding something | The form was not submitted (check the error message at the top of the page). |
| Data disappears | The database file was deleted or `EXPENSE_DB_PATH` points somewhere else. Check the path in `config.py`. |
| `sqlite3.OperationalError: unable to open database file` | The folder in `EXPENSE_DB_PATH` does not exist. Create it, or let the app create it. |

---

## 9. What comes next

| Phase | Content |
|-------|---------|
| 1 | **Done** - Flask app, SQLite, Bootstrap UI, tests, this README |
| 2 | Git repository, `.gitignore` review, push to GitHub |
| 3 | Terraform: Azure VM, network, Terraform variables/outputs/state |
| 4 | Jenkins pipeline: Checkout, Build, Test, Deploy (gunicorn + systemd), Health Check |
