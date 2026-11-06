import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from taskflow.database import initialize_database, list_tasks, create_task, set_task_completed, delete_task

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "taskflow.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "local-development-key")
app.config["DATABASE_PATH"] = DATABASE_PATH
initialize_database(DATABASE_PATH)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/tasks")
def get_tasks():
    return jsonify(list_tasks(app.config["DATABASE_PATH"]))


@app.post("/api/tasks")
def add_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify({"error": "El título es obligatorio."}), 400
    if len(title) > 120:
        return jsonify({"error": "El título no puede superar 120 caracteres."}), 400
    task = create_task(app.config["DATABASE_PATH"], title)
    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
def complete_task(task_id):
    task = set_task_completed(app.config["DATABASE_PATH"], task_id)
    if task is None:
        return jsonify({"error": "La tarea no existe."}), 404
    return jsonify(task)


@app.delete("/api/tasks/<int:task_id>")
def remove_task(task_id):
    if not delete_task(app.config["DATABASE_PATH"], task_id):
        return jsonify({"error": "La tarea no existe."}), 404
    return jsonify({"deleted": True})


if __name__ == "__main__":
    app.run(debug=True)
