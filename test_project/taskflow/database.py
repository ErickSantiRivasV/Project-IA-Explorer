import sqlite3
from pathlib import Path


def connect(database_path):
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path):
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def list_tasks(database_path):
    with connect(database_path) as connection:
        rows = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def create_task(database_path, title):
    with connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        row = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()
    return dict(row)


def set_task_completed(database_path, task_id):
    with connect(database_path) as connection:
        cursor = connection.execute(
            "UPDATE tasks SET completed = CASE completed WHEN 0 THEN 1 ELSE 0 END WHERE id = ?",
            (task_id,)
        )
        if cursor.rowcount == 0:
            return None
        row = connection.execute(
            "SELECT id, title, completed, created_at FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()
    return dict(row)


def delete_task(database_path, task_id):
    with connect(database_path) as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0
