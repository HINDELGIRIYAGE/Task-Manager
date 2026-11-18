# validation.py
# Small helper functions that check user input.
# Each one returns an error message, or None if the input is OK.

from datetime import datetime


def check_username(username):
    if not username:
        return "Please enter a username."
    if len(username) < 3 or len(username) > 20:
        return "Username must be 3-20 characters."
    if not username.replace("_", "").isalnum():
        return "Username can only use letters, numbers and _."
    return None


def check_password(password):
    if len(password) < 6:
        return "Password must be at least 6 characters."
    return None


def check_task(title, due_date):
    if not title.strip():
        return "Task title cannot be empty."
    if len(title) > 100:
        return "Task title must be 100 characters or less."
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return "Due date must look like YYYY-MM-DD (for example 2026-11-05)."
    return None


def check_category(name):
    if not name or not name.strip():
        return "Category name cannot be empty."
    if len(name.strip()) > 20:
        return "Category name must be 20 characters or less."
    return None
