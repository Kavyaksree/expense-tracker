"""Development entry point.

Run the application on your own machine with:

    python run.py

Then open http://127.0.0.1:5000 in a browser.
"""

from expense_tracker import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
