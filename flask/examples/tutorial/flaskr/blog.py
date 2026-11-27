from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required, save_uploaded_image
from flaskr.models import Post, db

bp = Blueprint("blog", __name__)

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def _validate_and_save_post_image(image_file):
    if not image_file or not image_file.filename:
        return None

    # Verifica o tamanho real do stream antes de processar
    image_file.stream.seek(0, 2)
    size = image_file.stream.tell()
    image_file.stream.seek(0)
    if size > MAX_IMAGE_BYTES:
        raise ValueError("A imagem do post excede o limite de 5 MB.")

    return save_uploaded_image(image_file)


def _remove_upload_if_exists(filename: str | None) -> None:
    if not filename:
        return
    upload_dir = Path(current_app.config.get("UPLOAD_FOLDER", ""))
    target = upload_dir / filename
    if target.is_file():
        target.unlink(missing_ok=True)


@bp.route("/")
def index():
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        image_file = request.files.get("imagem_post")
        error = None

        if not title:
            error = "Title is required."

        image_filename = None
        if error is None:
            try:
                image_filename = _validate_and_save_post_image(image_file)
            except ValueError as exc:
                error = str(exc)

        if error is not None:
            flash(error)
        else:
            post = Post(
                title=title,
                body=body,
                author_id=g.user.id,
                imagem_post=image_filename,
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_post(id, check_author=True):
    post = db.session.get(Post, id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post.author_id != g.user.id:
        abort(403)
    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        image_file = request.files.get("imagem_post")
        error = None

        if not title:
            error = "Title is required."

        new_image_name = None
        if error is None:
            try:
                new_image_name = _validate_and_save_post_image(image_file)
            except ValueError as exc:
                error = str(exc)

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            if new_image_name is not None:
                old_image = post.imagem_post
                post.imagem_post = new_image_name
                _remove_upload_if_exists(old_image)
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    old_image = post.imagem_post
    db.session.delete(post)
    db.session.commit()
    _remove_upload_if_exists(old_image)
    return redirect(url_for("blog.index"))