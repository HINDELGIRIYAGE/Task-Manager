# database.py
# All the SQLite database code for the TaskFlow app.

import hashlib
import os
import sqlite3
from datetime import datetime

# The database file is saved next to this file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

# Every new user gets these categories
DEFAULT_CATEGORIES = ["Study", "Work", "Personal"]


def hash_password(password, salt):
    # Mix the salt with the password and hash it with SHA-256
    return hashlib.sha256((salt + password).encode()).hexdigest()


class Database:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row          # lets us use row["title"]
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categories (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name    TEXT NOT NULL,
                UNIQUE(user_id, name)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                title       TEXT NOT NULL,
                description TEXT DEFAULT '',
                due_date    TEXT DEFAULT '',
                priority    TEXT DEFAULT 'Medium',
                status      TEXT DEFAULT 'Pending',
                created_at  TEXT NOT NULL
            );
        """)
        self.conn.commit()

    # ---------- Users ----------

    def register(self, username, password):
        # Returns the new user id, or None if the username is already taken
        taken = self.conn.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,)
        ).fetchone()
        if taken:
            return None

        salt = os.urandom(8).hex()
        cur = self.conn.execute(
            "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
            (username, hash_password(password, salt), salt),
        )
        user_id = cur.lastrowid

        # Give the new user the starter categories
        for name in DEFAULT_CATEGORIES:
            self.conn.execute(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, name)
            )
        self.conn.commit()
        return user_id

    def login(self, username, password):
        # Returns the user id if the username and password are correct, else None
        user = self.conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),)
        ).fetchone()
        if user and user["password"] == hash_password(password, user["salt"]):
            return user["id"]
        return None

    def get_username(self, user_id):
        user = self.conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        return user["username"] if user else ""

    # ---------- Categories ----------

    def get_categories(self, user_id):
        return self.conn.execute(
            "SELECT * FROM categories WHERE user_id = ? ORDER BY name", (user_id,)
        ).fetchall()

    def add_category(self, user_id, name):
        # Returns False if the user already has a category with this name
        try:
            self.conn.execute(
                "INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, name)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_category(self, category_id):
        # Tasks in this category are kept, they just lose their category
        self.conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()

    # ---------- Tasks ----------

    def add_task(self, user_id, title, description, category_id, due_date, priority):
        created = datetime.now().strftime("%Y-%m-%d %H:%M")
        cur = self.conn.execute(
            """INSERT INTO tasks (user_id, category_id, title, description,
                                  due_date, priority, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, category_id, title, description, due_date, priority, created),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_tasks(self, user_id, category_id=None, status=None, search=""):
        # Build the query step by step depending on the filters
        sql = """SELECT tasks.*, categories.name AS category
                 FROM tasks
                 LEFT JOIN categories ON tasks.category_id = categories.id
                 WHERE tasks.user_id = ?"""
        params = [user_id]

        if category_id:
            sql += " AND tasks.category_id = ?"
            params.append(category_id)
        if status:
            sql += " AND tasks.status = ?"
            params.append(status)
        if search:
            sql += " AND (tasks.title LIKE ? OR tasks.description LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]

        # Pending first, then High > Medium > Low, then by due date
        sql += """ ORDER BY tasks.status = 'Completed',
                   CASE tasks.priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END,
                   tasks.due_date = '', tasks.due_date"""
        return self.conn.execute(sql, params).fetchall()

    def get_task(self, task_id):
        return self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    def update_task(self, task_id, title, description, category_id, due_date, priority):
        self.conn.execute(
            """UPDATE tasks
               SET title = ?, description = ?, category_id = ?, due_date = ?, priority = ?
               WHERE id = ?""",
            (title, description, category_id, due_date, priority, task_id),
        )
        self.conn.commit()

    def set_status(self, task_id, status):
        self.conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        self.conn.commit()

    def delete_task(self, task_id):
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def count_tasks(self, user_id):
        # Returns (total, completed, pending)
        row = self.conn.execute(
            "SELECT COUNT(*) AS total, SUM(status = 'Completed') AS done "
            "FROM tasks WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        total = row["total"] or 0
        done = row["done"] or 0
        return total, done, total - done
