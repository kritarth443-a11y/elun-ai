import sqlite3
from datetime import datetime

def setup_database():
    # Connect to a local file (creates it automatically if it doesn't exist)
    conn = sqlite3.connect("creator_stats.db")
    cursor = conn.cursor()
    
    # Create a table to log every video's stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT,
            hook_delay REAL,
            wpm INTEGER,
            dead_air_spots INTEGER,
            date_analyzed TEXT
        )
    ''')
    conn.commit()
    return conn

def log_video_stats(video_name, hook_delay, wpm, dead_air_spots):
    conn = setup_database()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    cursor.execute('''
        INSERT INTO video_history (video_name, hook_delay, wpm, dead_air_spots, date_analyzed)
        VALUES (?, ?, ?, ?, ?)
    ''', (video_name, hook_delay, wpm, dead_air_spots, today))
    
    conn.commit()
    print(f"✅ Logged {video_name} to the tracker!")
    conn.close()

def view_history():
    conn = setup_database()
    cursor = conn.cursor()
    
    # Fetch the most recent 5 videos
    cursor.execute("SELECT video_name, hook_delay, wpm, date_analyzed FROM video_history ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    print("\n--- PAST UPLOADS PROGRESS ---")
    for row in rows:
        print(f"🎬 {row[0]} ({row[3]}) | Hook: {row[1]}s | Pace: {row[2]} WPM")
    conn.close()

if __name__ == "__main__":
    # 1. Simulating logging that rough first draft you just analyzed
    log_video_stats("draft_reel.mp4", 23.6, 60, 0)
    
    # 2. Simulating logging a better second attempt a day later
    log_video_stats("draft_reel_v2.mp4", 1.2, 145, 1)
    
    # 3. Show the history to prove the creator is improving
    view_history()