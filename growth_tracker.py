import sqlite3
from datetime import datetime

DB_PATH = "creator_stats.db"


def setup_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS video_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT,
            hook_delay REAL,
            wpm INTEGER,
            dead_air_spots INTEGER,
            date_analyzed TEXT
        )
    """)
    conn.commit()
    return conn


def log_video_stats(video_name, hook_delay, wpm, dead_air_spots):
    conn = setup_database()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn.execute(
        """
        INSERT INTO video_history (video_name, hook_delay, wpm, dead_air_spots, date_analyzed)
        VALUES (?, ?, ?, ?, ?)
        """,
        (video_name, hook_delay, wpm, dead_air_spots, now),
    )
    conn.commit()
    conn.close()
    print(f"✅ Logged {video_name} to the tracker!")


def view_history():
    conn = setup_database()
    rows = conn.execute(
        "SELECT video_name, hook_delay, wpm, date_analyzed "
        "FROM video_history ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()

    print("\n--- PAST UPLOADS PROGRESS ---")
    for name, hook, wpm, date in rows:
        print(f"🎬 {name} ({date}) | Hook: {hook}s | Pace: {wpm} WPM")


if __name__ == "__main__":
    log_video_stats("draft_reel.mp4", 23.6, 60, 0)
    log_video_stats("draft_reel_v2.mp4", 1.2, 145, 1)
    view_history()
