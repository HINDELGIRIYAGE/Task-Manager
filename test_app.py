# test_app.py
# Simple tests for the database and the input checks.
# Run with:  python -m unittest test_app.py

import unittest

from database import Database
from validation import check_category, check_password, check_task, check_username


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        # Use a fresh database in memory for every test
        self.db = Database(":memory:")
        self.user = self.db.register("nimal", "secret123")

    def test_register_and_login(self):
        self.assertEqual(self.db.login("nimal", "secret123"), self.user)
        self.assertIsNone(self.db.login("nimal", "wrong"))

    def test_username_must_be_unique(self):
        self.assertIsNone(self.db.register("Nimal", "another123"))

    def test_password_is_not_saved_as_plain_text(self):
        row = self.db.conn.execute("SELECT password FROM users").fetchone()
        self.assertNotEqual(row["password"], "secret123")

    def test_new_user_gets_default_categories(self):
        names = [c["name"] for c in self.db.get_categories(self.user)]
        self.assertEqual(names, ["Personal", "Study", "Work"])

    def test_add_edit_delete_task(self):
        task = self.db.add_task(self.user, "Write report", "", None, "2026-11-20", "High")
        self.assertEqual(len(self.db.get_tasks(self.user)), 1)

        self.db.update_task(task, "Write final report", "", None, "", "Low")
        self.assertEqual(self.db.get_task(task)["title"], "Write final report")

        self.db.set_status(task, "Completed")
        self.assertEqual(self.db.count_tasks(self.user), (1, 1, 0))

        self.db.delete_task(task)
        self.assertEqual(self.db.get_tasks(self.user), [])

    def test_search_and_filter(self):
        self.db.add_task(self.user, "Buy milk", "", None, "", "Low")
        done = self.db.add_task(self.user, "Read book", "", None, "", "Low")
        self.db.set_status(done, "Completed")

        self.assertEqual(len(self.db.get_tasks(self.user, search="milk")), 1)
        self.assertEqual(len(self.db.get_tasks(self.user, status="Completed")), 1)

    def test_deleting_category_keeps_tasks(self):
        category = self.db.get_categories(self.user)[0]["id"]
        self.db.add_task(self.user, "Gym", "", category, "", "Medium")
        self.db.delete_category(category)
        self.assertIsNone(self.db.get_tasks(self.user)[0]["category_id"])


class ValidationTests(unittest.TestCase):
    def test_username(self):
        self.assertIsNone(check_username("oshani_01"))
        self.assertIsNotNone(check_username("ab"))
        self.assertIsNotNone(check_username("bad name!"))

    def test_password(self):
        self.assertIsNone(check_password("123456"))
        self.assertIsNotNone(check_password("123"))

    def test_task(self):
        self.assertIsNone(check_task("Study", "2026-11-05"))
        self.assertIsNotNone(check_task("", ""))
        self.assertIsNotNone(check_task("Study", "05/11/2026"))

    def test_category(self):
        self.assertIsNone(check_category("Gym"))
        self.assertIsNotNone(check_category("   "))


if __name__ == "__main__":
    unittest.main()
