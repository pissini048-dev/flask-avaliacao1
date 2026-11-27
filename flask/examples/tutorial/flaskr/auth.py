import functools
import uuid
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from PIL import Image, UnidentifiedImageError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from flaskr.models import User, db

bp = Blueprint("auth", __name__, url_prefix="/auth")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    clean_name = secure_filename(file_storage.filename)
    if "." not in clean_name:
        raise ValueError("Arquivo sem extensão válida.")

    ext = clean_name.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Formato de imagem não permitido. Use PNG, JPG, JPEG, GIF ou WEBP."
        )

    try:
        file_storage.stream.seek(0)
        with Image.open(file_storage.stream) as img:
            img.verify()
        file_storage.stream.seek(0)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("O arquivo enviado não é uma imagem válida.") from exc

    unique_name = f"{uuid.uuid4().hex}_{clean_name}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_dir / unique_name)
    return unique_name


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        avatar_file = request.files.get("avatar")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        avatar_filename = None
        if error is None and avatar_file and avatar_file.filename:
            try:
                avatar_filename = save_uploaded_image(avatar_file)
            except ValueError as exc:
                error = str(exc)

        if error is None:
            user = User(
                username=username,
                password=generate_password_hash(password),
                avatar=avatar_filename,
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view