from flaskr.db import get_db

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