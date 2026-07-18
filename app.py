from flask import Flask

from config import Config
from database.db import db
from database.seed import seed_database


def create_app():
    """
    Application factory. Building the app this way (instead of a bare
    module-level `app = Flask(...)`) makes it easier to test and to
    create multiple configured instances later if needed.
    """
    app = Flask(__name__, static_folder="static", static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)

    # API routes: /api/buses (CRUD), /api/search, /api/live
    from routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        # Import models here so SQLAlchemy knows about them before create_all().
        from models.bus import Bus  # noqa: F401

        db.create_all()
        seed_database()

    # Serves your existing frontend as the homepage.
    # script.js and images/ are served automatically from static/
    # since static_url_path="" maps the static folder to the site root.
    @app.route("/")
    def serve_index():
        return app.send_static_file("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
