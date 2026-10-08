import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, flash, abort
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
PRIORITIES = ("Low", "Medium", "High")


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        DATABASE=os.path.join(app.root_path, "tasks.db"),
    )
    csrf.init_app(app)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db:
            db.close()

    def init_db():
        with app.app_context():
            get_db().execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT NOT NULL DEFAULT 'Medium',
                    due_date TEXT,
                    done INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            get_db().commit()

    def get_task(task_id):
        task = get_db().execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task is None:
            abort(404)
        return task

    def read_form():
        title = request.form.get("title", "").strip()
        desc = request.form.get("description", "").strip()
        prio = request.form.get("priority", "Medium")
        due = request.form.get("due_date") or None
        error = None
        if not title:
            error = "Title is required."
        elif len(title) > 100:
            error = "Title must be 100 characters or fewer."
        elif prio not in PRIORITIES:
            error = "Invalid priority."
        return title, desc, prio, due, error

    @app.route("/")
    def index():
        flt = request.args.get("filter", "all")
        q = request.args.get("q", "").strip()
        sql, params = "SELECT * FROM tasks WHERE 1=1", []
        if flt == "active":
            sql += " AND done = 0"
        elif flt == "done":
            sql += " AND done = 1"
        if q:
            sql += " AND (title LIKE ? OR description LIKE ?)"
            params += [f"%{q}%", f"%{q}%"]
        sql += """ ORDER BY done ASC,
                   CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
                   due_date IS NULL, due_date"""
        db = get_db()
        tasks = db.execute(sql, params).fetchall()
        stats = db.execute(
            "SELECT COUNT(*) total, COALESCE(SUM(done),0) done FROM tasks"
        ).fetchone()
        pct = round(stats["done"] / stats["total"] * 100) if stats["total"] else 0
        return render_template("index.html", tasks=tasks, stats=stats, pct=pct,
                               flt=flt, q=q, priorities=PRIORITIES)

    @app.post("/add")
    def add():
        title, desc, prio, due, error = read_form()
        if error:
            flash(error, "error")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (title, description, priority, due_date) VALUES (?,?,?,?)",
                (title, desc, prio, due),
            )
            db.commit()
            flash("Task added.", "success")
        return redirect(url_for("index"))

    @app.route("/edit/<int:task_id>", methods=("GET", "POST"))
    def edit(task_id):
        task = get_task(task_id)
        if request.method == "POST":
            title, desc, prio, due, error = read_form()
            if error:
                flash(error, "error")
            else:
                db = get_db()
                db.execute(
                    "UPDATE tasks SET title=?, description=?, priority=?, due_date=? WHERE id=?",
                    (title, desc, prio, due, task_id),
                )
                db.commit()
                flash("Task updated.", "success")
                return redirect(url_for("index"))
        return render_template("edit.html", task=task, priorities=PRIORITIES)

    @app.post("/toggle/<int:task_id>")
    def toggle(task_id):
        get_task(task_id)
        db = get_db()
        db.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
        db.commit()
        return redirect(request.referrer or url_for("index"))

    @app.post("/delete/<int:task_id>")
    def delete(task_id):
        get_task(task_id)
        db = get_db()
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        flash("Task deleted.", "success")
        return redirect(request.referrer or url_for("index"))

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("base.html", not_found=True), 404

    init_db()
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
