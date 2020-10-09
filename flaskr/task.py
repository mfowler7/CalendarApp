import datetime
import flaskr.repositories.task_repository as task_repo

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
    # TODO: Remove this once taskType is available via URL
    tasks = task_repo.get_all_tasks()

    # switch (taskType) {
    #     case "all":
    #         tasks = get_all_tasks()
    #     case "today":
    #         tasks = get_todays_tasks()
    #     case "unplanned":
    #         tasks = get_unplanned_tasks()
    #     default:
    #         tasks = get_all_tasks() 
    # }

    print(f"Length of tasks: {len(tasks)}")
    return render_template("task/index.html", tasks=tasks)


def get_task(id, check_user=True):
    task = task_repo.get_task(id)

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
        desc = request.form["description"]
        prio = request.form["priority"]
        scheduled = request.form["scheduled"]

        error = None
        if not name:
            error = "Task name is required."

        if error is not None:
            flash(error)
        else:
            task_repo.create(name, desc, prio, scheduled)
            return redirect(url_for("task.index"))

    return render_template("task/create.html")


@bp.route("/task/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    task = get_task(id)

    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["description"]
        prio = request.form["priority"]
        scheduled = request.form["scheduled"]

        error = None
        if not name:
            error = "Task name is required."

        if error is not None:
            flash(error)
        else:
            task_repo.update(name, desc, prio, scheduled)
            return redirect(url_for("task.index"))

    return render_template("task/update.html", task=task)


@bp.route("/task/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    task_repo.delete(id)
    return redirect(url_for("task.index"))


# TODO: Remove this, make it a dropdown on the main task
@bp.route("/task/<int:id>/details", methods=("GET",))
@login_required
def details(id):
    task = get_task(id)
    return render_template("task/details.html", task=task)