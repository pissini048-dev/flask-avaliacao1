import os
from pathlib import Path

from flask import Flask

from flaskr.models import db


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    upload_folder = Path(app.root_path) / "static" / "uploads"
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(upload_folder, exist_ok=True)

    db_path = Path(app.instance_path) / "flaskr.sqlite"

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(upload_folder),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        from flaskr import models  # noqa: F401

        db.create_all()

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from . import auth, blog, calculos

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(calculos.bp)

    app.add_url_rule("/", endpoint="index")

    return app