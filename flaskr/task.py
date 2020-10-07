import datetime
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
    tasks = get_all_tasks()
    return render_template("task/index.html", tasks=tasks)

@bp.route("/tasks/today")
def today():
    tasks = get_todays_tasks()
    return render_template("task/index.html", tasks=tasks)

@bp.route("/tasks/unplanned")
def unplanned():
    tasks = get_unplanned_tasks()
    return render_template("task/index.html", tasks=tasks)

def get_task(id, check_user=True):
    task = (
        get_db()
        .execute(
            "SELECT t.id, name, description, created, scheduled, priority, user_id, username"
            " FROM task t JOIN user u ON t.user_id = u.id"
            " WHERE t.id = ?",
            (id,),
        ).fetchone()
    )

    if task is None:
        abort(404, "Task id {0} doesn't exist.".format(id))

    if check_user and task["user_id"] != g.user["id"]:
        abort(403)

    return task

def get_all_tasks():
    tasks = (
        get_db()
        .execute(
            "SELECT t.id, name, description, created, scheduled, priority, user_id, username"
            " FROM task t JOIN user u ON t.user_id = u.id",
        ).fetchall()
    )

    return tasks

def get_unplanned_tasks():
    unplanned_tasks = (
        get_db()
        .execute(
            "SELECT t.id, name, description, created, scheduled, priority, user_id, username"
            " FROM task t JOIN user u ON t.user_id = u.id"
            " WHERE scheduled IS NULL",
        ).fetchall()
    )

    return unplanned_tasks

def get_todays_tasks():
    today = datetime.datetime.now().strftime("%m-%d-%Y") + " 00:00:00"
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    tomorrow_formatted = tomorrow.strftime("%m-%d-%Y") + " 00:00:00"

    print("Tomorrow: {}".format(tomorrow_formatted))

    db = get_db()
    tasks = db.execute(
        "SELECT t.id, name, description, created, user_id, username"
        " FROM task t JOIN user u ON t.user_id = u.id"
        " WHERE scheduled >= '{}'".format(today)
    ).fetchall()

    return tasks

@bp.route("/task/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        priority = request.form["priority"]

        if request.form["scheduled"] != '':
            scheduled = datetime.datetime.strptime(request.form["scheduled"], '%Y-%m-%d')
        else:
            scheduled = None
            
        error = None

        if not name:
            error = "Task name is required."

        if error is not None:
            flash(error)
        else:
            if scheduled != '':
                db = get_db()
                db.execute(
                    "INSERT INTO task (name, description, user_id, priority, scheduled) VALUES (?, ?, ?, ?, ?)",
                    (name, description, g.user["id"], priority, scheduled,),
                )
                db.commit()
            else:
                db = get_db()
                db.execute(
                    "INSERT INTO task (name, description, user_id, priority, scheduled) VALUES (?, ?, ?, ?)",
                    (name, description, g.user["id"], priority,),
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
        priority = request.form["priority"]
        scheduled = request.form["scheduled"]  + " 00:00:00"
        error = None

        print("Scheduled: {}".format(scheduled))

        if not name:
            error = "Task name is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE task SET name = ?, description = ?, priority = ?, scheduled = ? WHERE id = ?", (name, description, priority, scheduled, id)
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

    return render_template("task/details.html", task=task)