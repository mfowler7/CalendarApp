from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("task", __name__)


@bp.route("/tasks")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    tasks = db.execute(
        "SELECT t.id, name, description, created, user_id, username"
        " FROM task t JOIN user u ON t.user_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("task/index.html", tasks=tasks)


def get_task(id, check_user=True):
    """Get a task and its user by id.
    Checks that the id exists and optionally that the current user is
    the task owner.
    :param id: id of task to get
    :param check_user: require the current user to be the task owner
    :return: the task with user information
    :raise 404: if a task with the given id doesn't exist
    :raise 403: if the current user isn't the task owner
    """
    task = (
        get_db()
        .execute(
            "SELECT t.id, name, description, created, user_id, username"
            " FROM task t JOIN user u ON t.user_id = u.id"
            " WHERE t.id = ?",
            (id,),
        )
        .fetchone()
    )

    if task is None:
        abort(404, "Task id {0} doesn't exist.".format(id))

    if check_user and task["user_id"] != g.user["id"]:
        abort(403)

    return task


@bp.route("/task/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        error = None

        if not name:
            error = "Task name is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO task (name, description, user_id) VALUES (?, ?, ?)",
                (name, description, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("task.index"))

    return render_template("task/create.html")


@bp.route("/task/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a task if the current user is the task owner."""
    task = get_task(id)

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        error = None

        if not name:
            error = "Task name is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE task SET name = ?, description = ? WHERE id = ?", (name, description, id)
            )
            db.commit()
            return redirect(url_for("task.index"))

    return render_template("task/update.html", task=task)


@bp.route("/task/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a task.
    Ensures that the task exists and that the logged in user is the
    owner of the task.
    """
    get_task(id)
    db = get_db()
    db.execute("DELETE FROM task WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("task.index"))

@bp.route("/task/<int:id>/details", methods=("GET",))
@login_required
def details(id):
    """ Display all the data associated with the task """
    task = get_task(id)

    render_template("task.details", task=task)