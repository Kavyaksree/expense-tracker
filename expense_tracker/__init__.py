"""Expense Tracker application package.

The application is built with an *application factory* (``create_app``).
Instead of a global ``app`` object, we create a fresh application each time
we need one. That makes testing easy, because every test can use its own
temporary database without touching your real data.
"""

from flask import Flask

from .config import BASE_DIR, Config
from .db import close_db, init_db
from .routes import main_bp
from .validation import format_cents


def create_app(test_config=None):
    """Create and configure the Flask application.

    Args:
        test_config: Optional dictionary of settings that override the
            defaults (used by the test suite, for example to point the
            database at a temporary file).
    """
    # The templates and static files live in the project root, not inside the
    # package folder, so we point Flask at them explicitly.
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    # 1. Load the default settings from config.py.
    app.config.from_object(Config)

    # 2. Apply any overrides (for example from the test suite).
    if test_config:
        app.config.update(test_config)

    # 3. Make sure the database file and table exist.
    init_db(app)

    # 4. Register the routes and the database cleanup handler.
    app.register_blueprint(main_bp)
    app.teardown_appcontext(close_db)

    # 5. Helper used in the templates: {{ 1250 | money("$") }} -> "$12.50".
    app.jinja_env.filters["money"] = format_cents

    return app
