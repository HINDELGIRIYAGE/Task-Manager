# main.py
# TaskFlow - a simple desktop task manager
# Built with Python, Tkinter and SQLite
#
# Run it with:  python main.py

import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk

from database import Database
from validation import check_category, check_password, check_task, check_username

PRIORITIES = ["High", "Medium", "Low"]

# Colours used in the app
BG = "#0b1410"         # window background
CARD = "#12201a"       # panels and forms
ACCENT = "#22c55e"     # green buttons and headings
TEXT = "#e6f4ea"       # normal text
MUTED = "#7f9b8a"      # small grey text
RED = "#ef4444"        # overdue / delete
ORANGE = "#f59e0b"     # high priority
FONT = "Segoe UI"


def setup_style(root):
    # Give the ttk widgets a simple dark green look
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=TEXT, font=(FONT, 10))
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("Small.TLabel", background=CARD, foreground=MUTED, font=(FONT, 9))
    style.configure("Title.TLabel", background=CARD, foreground=ACCENT, font=(FONT, 18, "bold"))
    style.configure("Heading.TLabel", background=BG, foreground=ACCENT, font=(FONT, 15, "bold"))
    style.configure("TCheckbutton", background=CARD, foreground=MUTED)
    style.map("TCheckbutton", background=[("active", CARD)])

    border = dict(bordercolor="#1f3a2c", lightcolor="#1f3a2c", darkcolor="#1f3a2c")
    style.configure("TEntry", fieldbackground="#0f1a15", foreground=TEXT, insertcolor=TEXT, **border)
    style.map("TEntry", bordercolor=[("focus", ACCENT)])
    style.configure("TCombobox", fieldbackground="#0f1a15", foreground=TEXT,
                    background=CARD, arrowcolor=ACCENT, **border)
    style.map("TCombobox", fieldbackground=[("readonly", "#0f1a15")], foreground=[("readonly", TEXT)])

    style.configure("TButton", background=CARD, foreground=TEXT, padding=(12, 6), borderwidth=0)
    style.map("TButton", background=[("active", "#1c3127")])
    style.configure("Green.TButton", background=ACCENT, foreground="#05110a", font=(FONT, 10, "bold"))
    style.map("Green.TButton", background=[("active", "#16a34a")])
    style.configure("Red.TButton", background=CARD, foreground=RED)
    style.map("Red.TButton", background=[("active", "#3a1515")])

    style.configure("Treeview", background=CARD, fieldbackground=CARD, foreground=TEXT,
                    rowheight=28, **border)
    style.configure("Treeview.Heading", background="#1c3127", foreground=ACCENT,
                    font=(FONT, 10, "bold"), relief="flat", **border)
    style.map("Treeview.Heading", background=[("active", "#24402f")])
    style.map("Treeview", background=[("selected", "#1f6f43")])


# ------------------------------------------------------------
# Login screen
# ------------------------------------------------------------
class LoginScreen(ttk.Frame):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app

        card = ttk.Frame(self, style="Card.TFrame", padding=32)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="TaskFlow", style="Title.TLabel").pack(anchor="w")
        ttk.Label(card, text="Log in to manage your tasks", style="Small.TLabel").pack(anchor="w", pady=(0, 18))

        ttk.Label(card, text="Username", style="Card.TLabel").pack(anchor="w")
        self.username = ttk.Entry(card, width=30)
        self.username.pack(fill="x", pady=(2, 10), ipady=3)

        ttk.Label(card, text="Password", style="Card.TLabel").pack(anchor="w")
        self.password = ttk.Entry(card, width=30, show="*")
        self.password.pack(fill="x", pady=(2, 4), ipady=3)

        # Tick box to show or hide the password
        self.show_password = tk.BooleanVar()
        ttk.Checkbutton(card, text="Show password", variable=self.show_password,
                        command=self.toggle_password).pack(anchor="w", pady=(0, 14))

        ttk.Button(card, text="Log in", style="Green.TButton", command=self.login).pack(fill="x")
        ttk.Button(card, text="Create new account", command=self.open_register).pack(fill="x", pady=(8, 0))

        self.username.focus()
        self.password.bind("<Return>", lambda event: self.login())

    def toggle_password(self):
        self.password.config(show="" if self.show_password.get() else "*")

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            messagebox.showwarning("Login", "Please enter your username and password.")
            return

        user_id = self.app.db.login(username, password)
        if user_id is None:
            messagebox.showerror("Login", "Wrong username or password.")
            return
        self.app.show_dashboard(user_id)

    def open_register(self):
        window = RegisterWindow(self, self.app.db)
        self.wait_window(window)
        if window.new_user_id:
            self.app.show_dashboard(window.new_user_id)


class RegisterWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.new_user_id = None
        self.title("Create account")
        self.configure(bg=CARD)
        self.resizable(False, False)

        body = ttk.Frame(self, style="Card.TFrame", padding=24)
        body.pack()

        ttk.Label(body, text="Create account", style="Title.TLabel").pack(anchor="w", pady=(0, 14))

        ttk.Label(body, text="Username", style="Card.TLabel").pack(anchor="w")
        self.username = ttk.Entry(body, width=30)
        self.username.pack(fill="x", pady=(2, 10), ipady=3)

        ttk.Label(body, text="Password (at least 6 characters)", style="Card.TLabel").pack(anchor="w")
        self.password = ttk.Entry(body, width=30, show="*")
        self.password.pack(fill="x", pady=(2, 10), ipady=3)

        ttk.Label(body, text="Confirm password", style="Card.TLabel").pack(anchor="w")
        self.confirm = ttk.Entry(body, width=30, show="*")
        self.confirm.pack(fill="x", pady=(2, 16), ipady=3)

        ttk.Button(body, text="Create account", style="Green.TButton", command=self.create).pack(fill="x")

        self.username.focus()
        self.grab_set()   # keep focus on this window until it is closed

    def create(self):
        username = self.username.get().strip()
        password = self.password.get()

        error = check_username(username) or check_password(password)
        if not error and password != self.confirm.get():
            error = "The two passwords do not match."
        if error:
            messagebox.showwarning("Create account", error, parent=self)
            return

        user_id = self.db.register(username, password)
        if user_id is None:
            messagebox.showerror("Create account", "That username is already taken.", parent=self)
            return

        self.new_user_id = user_id
        self.destroy()


# ------------------------------------------------------------
# Add / Edit task form
# ------------------------------------------------------------
class TaskForm(tk.Toplevel):
    def __init__(self, parent, categories, task=None):
        super().__init__(parent)
        self.categories = categories
        self.result = None
        self.title("Edit task" if task else "Add task")
        self.configure(bg=CARD)
        self.resizable(False, False)

        body = ttk.Frame(self, style="Card.TFrame", padding=22)
        body.pack()

        ttk.Label(body, text=self.title(), style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Label(body, text="Title", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.title_entry = ttk.Entry(body, width=34)
        self.title_entry.grid(row=1, column=1, pady=5, ipady=2)

        ttk.Label(body, text="Description", style="Card.TLabel").grid(row=2, column=0, sticky="nw", pady=5)
        self.description = tk.Text(body, width=34, height=4, bg="#0f1a15", fg=TEXT,
                                   insertbackground=TEXT, relief="flat", font=(FONT, 10))
        self.description.grid(row=2, column=1, pady=5)

        ttk.Label(body, text="Category", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        self.category = ttk.Combobox(body, state="readonly", width=32,
                                     values=["(none)"] + [c["name"] for c in categories])
        self.category.grid(row=3, column=1, pady=5)
        self.category.current(0)

        ttk.Label(body, text="Due date", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=5)
        self.due_date = ttk.Entry(body, width=34)
        self.due_date.grid(row=4, column=1, pady=5, ipady=2)
        ttk.Label(body, text="YYYY-MM-DD, optional", style="Small.TLabel").grid(row=5, column=1, sticky="w")

        ttk.Label(body, text="Priority", style="Card.TLabel").grid(row=6, column=0, sticky="w", pady=5)
        self.priority = ttk.Combobox(body, state="readonly", width=32, values=PRIORITIES)
        self.priority.grid(row=6, column=1, pady=5)
        self.priority.set("Medium")

        ttk.Button(body, text="Save", style="Green.TButton", command=self.save).grid(
            row=7, column=1, sticky="e", pady=(14, 0))

        # When editing, fill the form with the task's current values
        if task:
            self.title_entry.insert(0, task["title"])
            self.description.insert("1.0", task["description"] or "")
            self.due_date.insert(0, task["due_date"] or "")
            self.priority.set(task["priority"])
            self.select_category(task["category_id"])

        self.title_entry.focus()
        self.grab_set()

    def select_category(self, category_id):
        for i, category in enumerate(self.categories, start=1):
            if category["id"] == category_id:
                self.category.current(i)

    def save(self):
        title = self.title_entry.get().strip()
        due_date = self.due_date.get().strip()

        error = check_task(title, due_date)
        if error:
            messagebox.showwarning("Task", error, parent=self)
            return

        index = self.category.current()
        category_id = self.categories[index - 1]["id"] if index > 0 else None

        self.result = {
            "title": title,
            "description": self.description.get("1.0", "end").strip(),
            "category_id": category_id,
            "due_date": due_date,
            "priority": self.priority.get(),
        }
        self.destroy()


# ------------------------------------------------------------
# Main dashboard
# ------------------------------------------------------------
class Dashboard(ttk.Frame):
    def __init__(self, app, user_id):
        super().__init__(app.root)
        self.app = app
        self.db = app.db
        self.user_id = user_id
        self.category_ids = [None]   # None means "All tasks"

        # ----- left side: categories -----
        side = ttk.Frame(self, style="Card.TFrame", padding=16)
        side.pack(side="left", fill="y")

        ttk.Label(side, text="TaskFlow", style="Title.TLabel").pack(anchor="w")
        ttk.Label(side, text="Hi, " + self.db.get_username(user_id), style="Small.TLabel").pack(anchor="w", pady=(0, 16))

        ttk.Label(side, text="Categories", style="Card.TLabel").pack(anchor="w")
        self.category_list = tk.Listbox(side, width=22, height=12, bg=CARD, fg=TEXT,
                                        selectbackground="#1f6f43", relief="flat",
                                        highlightthickness=0, font=(FONT, 10), activestyle="none")
        self.category_list.pack(fill="y", expand=True, pady=6)
        self.category_list.bind("<<ListboxSelect>>", lambda event: self.refresh_tasks())

        ttk.Button(side, text="+ Add category", command=self.add_category).pack(fill="x")
        ttk.Button(side, text="Delete category", command=self.delete_category).pack(fill="x", pady=(6, 0))
        ttk.Button(side, text="Log out", style="Red.TButton", command=app.show_login).pack(fill="x", pady=(18, 0))

        # ----- right side: tasks -----
        main = ttk.Frame(self, padding=18)
        main.pack(side="left", fill="both", expand=True)

        top = ttk.Frame(main)
        top.pack(fill="x")
        self.heading = ttk.Label(top, text="All tasks", style="Heading.TLabel")
        self.heading.pack(side="left")
        self.stats = ttk.Label(top, foreground=MUTED)
        self.stats.pack(side="right")

        # Search box and status filter
        filters = ttk.Frame(main)
        filters.pack(fill="x", pady=12)
        ttk.Label(filters, text="Search").pack(side="left")
        self.search_text = tk.StringVar()
        self.search_text.trace_add("write", lambda *args: self.refresh_tasks())
        ttk.Entry(filters, textvariable=self.search_text, width=28).pack(side="left", padx=(6, 18))

        ttk.Label(filters, text="Status").pack(side="left")
        self.status_filter = ttk.Combobox(filters, state="readonly", width=12,
                                          values=["All", "Pending", "Completed"])
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=6)
        self.status_filter.bind("<<ComboboxSelected>>", lambda event: self.refresh_tasks())

        # Task table
        columns = ("title", "category", "priority", "due", "status")
        self.table = ttk.Treeview(main, columns=columns, show="headings", selectmode="browse")
        for column, heading, width in [("title", "Task", 260), ("category", "Category", 110),
                                       ("priority", "Priority", 80), ("due", "Due date", 100),
                                       ("status", "Status", 100)]:
            self.table.heading(column, text=heading)
            self.table.column(column, width=width, anchor="w" if column == "title" else "center")
        self.table.pack(fill="both", expand=True)

        # Colours for special rows
        self.table.tag_configure("done", foreground=MUTED)
        self.table.tag_configure("overdue", foreground=RED)
        self.table.tag_configure("high", foreground=ORANGE)

        self.table.bind("<Double-1>", lambda event: self.edit_task())

        # Buttons under the table
        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(12, 0))
        ttk.Button(buttons, text="+ Add task", style="Green.TButton", command=self.add_task).pack(side="left")
        ttk.Button(buttons, text="Edit", command=self.edit_task).pack(side="left", padx=6)
        ttk.Button(buttons, text="Done / Undo", command=self.toggle_status).pack(side="left")
        ttk.Button(buttons, text="Delete", style="Red.TButton", command=self.delete_task).pack(side="right")

        self.load_categories()
        self.refresh_tasks()

    # ----- categories -----

    def load_categories(self):
        self.category_list.delete(0, "end")
        self.category_ids = [None]
        self.category_list.insert("end", "All tasks")
        for category in self.db.get_categories(self.user_id):
            self.category_list.insert("end", category["name"])
            self.category_ids.append(category["id"])
        self.category_list.selection_set(0)

    def selected_category(self):
        selected = self.category_list.curselection()
        if not selected:
            return None
        return self.category_ids[selected[0]]

    def add_category(self):
        name = simpledialog.askstring("New category", "Category name:", parent=self)
        if name is None:
            return
        error = check_category(name)
        if error:
            messagebox.showwarning("Category", error)
            return
        if not self.db.add_category(self.user_id, name.strip()):
            messagebox.showwarning("Category", "You already have that category.")
            return
        self.load_categories()
        self.refresh_tasks()

    def delete_category(self):
        category_id = self.selected_category()
        if category_id is None:
            messagebox.showinfo("Category", "Select a category to delete first.")
            return
        if messagebox.askyesno("Delete category", "Delete this category?\nIts tasks will be kept."):
            self.db.delete_category(category_id)
            self.load_categories()
            self.refresh_tasks()

    # ----- tasks -----

    def refresh_tasks(self):
        self.table.delete(*self.table.get_children())

        status = self.status_filter.get()
        tasks = self.db.get_tasks(
            self.user_id,
            category_id=self.selected_category(),
            status=None if status == "All" else status,
            search=self.search_text.get().strip(),
        )

        today = date.today().isoformat()
        for task in tasks:
            status_text = task["status"]
            tag = ""
            if task["status"] == "Completed":
                tag = "done"
            elif task["due_date"] and task["due_date"] < today:
                tag = "overdue"
                status_text = "Overdue"
            elif task["priority"] == "High":
                tag = "high"

            self.table.insert("", "end", iid=str(task["id"]), tags=(tag,), values=(
                task["title"], task["category"] or "-", task["priority"],
                task["due_date"] or "-", status_text))

        # Update the heading and the small task counter
        selected = self.category_list.curselection()
        self.heading.config(text=self.category_list.get(selected[0]) if selected else "All tasks")
        total, done, pending = self.db.count_tasks(self.user_id)
        self.stats.config(text=f"Total {total}   Done {done}   Pending {pending}")

    def selected_task_id(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Task", "Select a task in the table first.")
            return None
        return int(selected[0])

    def add_task(self):
        form = TaskForm(self, self.db.get_categories(self.user_id))
        form.select_category(self.selected_category())
        self.wait_window(form)
        if form.result:
            self.db.add_task(self.user_id, **form.result)
            self.refresh_tasks()

    def edit_task(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        form = TaskForm(self, self.db.get_categories(self.user_id), self.db.get_task(task_id))
        self.wait_window(form)
        if form.result:
            self.db.update_task(task_id, **form.result)
            self.refresh_tasks()

    def toggle_status(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        task = self.db.get_task(task_id)
        new_status = "Pending" if task["status"] == "Completed" else "Completed"
        self.db.set_status(task_id, new_status)
        self.refresh_tasks()

    def delete_task(self):
        task_id = self.selected_task_id()
        if task_id is None:
            return
        if messagebox.askyesno("Delete task", "Are you sure you want to delete this task?"):
            self.db.delete_task(task_id)
            self.refresh_tasks()


# ------------------------------------------------------------
# App - switches between the login screen and the dashboard
# ------------------------------------------------------------
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TaskFlow")
        self.root.geometry("980x600")
        self.root.minsize(820, 500)
        self.root.configure(bg=BG)
        setup_style(self.root)

        self.db = Database()
        self.screen = None
        self.show_login()

    def show_screen(self, screen):
        if self.screen:
            self.screen.destroy()
        self.screen = screen
        self.screen.pack(fill="both", expand=True)

    def show_login(self):
        self.show_screen(LoginScreen(self))

    def show_dashboard(self, user_id):
        self.show_screen(Dashboard(self, user_id))


if __name__ == "__main__":
    App().root.mainloop()
