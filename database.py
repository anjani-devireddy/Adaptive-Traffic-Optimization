import sqlite3
from pathlib import Path
from datetime import datetime

from config import BASE_DIR


DB_PATH = BASE_DIR / "data" / "traffic.db"


def get_connection():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            camera_id INTEGER NOT NULL,
            vehicle_count INTEGER NOT NULL,
            weighted_score REAL NOT NULL,
            density REAL NOT NULL,
            green_time INTEGER NOT NULL,
            signal_color TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_traffic_record(
    camera_id,
    vehicle_count,
    weighted_score,
    density,
    green_time,
    signal_color
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO traffic_history (
            timestamp,
            camera_id,
            vehicle_count,
            weighted_score,
            density,
            green_time,
            signal_color
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(
                timespec="seconds"
            ),
            camera_id,
            vehicle_count,
            weighted_score,
            density,
            green_time,
            signal_color,
        )
    )

    connection.commit()
    connection.close()


def get_recent_records(limit=100):

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM traffic_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]