import os
import sqlite3
from pathlib import Path
from typing import List, Dict

DB_PATH = Path(__file__).resolve().parent / "students.db"
ROOM_CAPACITY = 25


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            register_number TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            room_number INTEGER NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def import_students(rows: List[Dict[str, str]], department: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    existing = {row[0] for row in cursor.execute("SELECT register_number FROM students")}
    for index, row in enumerate(rows, start=1):
        reg_no = row.get("register_number") or ""
        if not reg_no:
            continue
        if reg_no in existing:
            continue
        room_number = ((index - 1) // ROOM_CAPACITY) + 1
        cursor.execute(
            "INSERT INTO students (name, register_number, department, room_number) VALUES (?, ?, ?, ?)",
            (row.get("name", ""), reg_no, department, room_number),
        )
        existing.add(reg_no)
    conn.commit()
    conn.close()


def remove_student(register_number: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE students SET is_active = 0 WHERE register_number = ?", (register_number,))
    conn.commit()
    conn.close()


def get_students(department: str | None = None) -> List[Dict[str, object]]:
    conn = sqlite3.connect(DB_PATH)
    if department:
        rows = conn.execute(
            "SELECT name, register_number, department, room_number, is_active FROM students WHERE department = ? ORDER BY room_number, id",
            (department,),
        )
    else:
        rows = conn.execute(
            "SELECT name, register_number, department, room_number, is_active FROM students ORDER BY room_number, id"
        )
    results = [
        {
            "name": row[0],
            "register_number": row[1],
            "department": row[2],
            "room_number": row[3],
            "is_active": row[4],
        }
        for row in rows.fetchall()
    ]
    conn.close()
    return results


def get_room_summary() -> List[Dict[str, object]]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT room_number, COUNT(*) AS total FROM students WHERE is_active = 1 GROUP BY room_number ORDER BY room_number"
    ).fetchall()
    conn.close()
    return [{"room_number": room, "total": total} for room, total in rows]


if __name__ == "__main__":
    print("Student room allocation app is ready")
