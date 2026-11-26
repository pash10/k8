import os
import secrets

from flask import Flask
from dym_form import form_view

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    MAX_CONTENT_LENGTH=16 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)
app.add_url_rule("/", view_func=form_view, methods=["GET", "POST"])

if __name__ == "__main__":
    # Local prototype only; do not expose the development server.
    app.run(host="127.0.0.1", debug=False)
