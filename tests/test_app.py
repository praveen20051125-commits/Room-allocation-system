import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_students.db"
        app.DB_PATH = self.db_path
        app.init_db()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_room_assignment_for_26_students(self):
        rows = [
            {"name": f"Student {i}", "register_number": f"REG{i}", "department": "CSE"}
            for i in range(1, 27)
        ]
        app.import_students(rows, department="CSE")
        conn = sqlite3.connect(self.db_path)
        students = conn.execute("SELECT room_number FROM students ORDER BY id").fetchall()
        conn.close()
        self.assertEqual(students[0][0], 1)
        self.assertEqual(students[24][0], 1)
        self.assertEqual(students[25][0], 2)

    def test_manual_removal_marks_student_inactive(self):
        app.import_students([
            {"name": "Alice", "register_number": "REG1", "department": "ECE"}
        ], department="ECE")
        app.remove_student("REG1")
        conn = sqlite3.connect(self.db_path)
        active = conn.execute("SELECT is_active FROM students WHERE register_number = ?", ("REG1",)).fetchone()[0]
        conn.close()
        self.assertEqual(active, 0)


if __name__ == "__main__":
    unittest.main()
