from flaskr.db import get_db


# Create Methods
def create(name, desc, prio, scheduled):
    if scheduled:
        # Is a date, leave it
        scheduled = datetime.datetime.strptime(request.form["scheduled"], '%Y-%m-%d')
    else:
        scheduled = None

    db = get_db()
    db.execute(
        "INSERT INTO task (name, description, user_id, priority, scheduled) VALUES (?, ?, ?, ?, ?)",
        (name, description, g.user["id"], priority, scheduled,),
    )
    db.commit()


# Read Methods
def get_task(id):
    task = (
        get_db()
        .execute(
            "SELECT t.id, name, description, created, scheduled, priority, user_id, username"
            " FROM task t JOIN user u ON t.user_id = u.id"
            " WHERE t.id = ?",
            (id,),
        ).fetchone()
    )

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

    db = get_db()
    tasks = db.execute(
        "SELECT t.id, name, description, created, user_id, username"
        " FROM task t JOIN user u ON t.user_id = u.id"
        " WHERE scheduled IS NOT NULL AND scheduled >= '{}'".format(today)
    ).fetchall()

    return tasks


# Update Methods
def update(name, desc, prio, scheduled):
    db = get_db()
    db.execute(
        "UPDATE task SET name = ?, description = ?, priority = ?, scheduled = ? WHERE id = ?", (name, description, priority, scheduled, id)
    )
    db.commit()


# Delete Methods
def delete(id):
    db = get_db()
    db.execute("DELETE FROM task WHERE id = ?", (id,))
    db.commit()