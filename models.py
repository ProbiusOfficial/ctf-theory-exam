import sqlite3
import json
import os
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            score REAL NOT NULL,
            max_score REAL NOT NULL,
            time_spent INTEGER NOT NULL,
            answers TEXT NOT NULL,
            exam_questions TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_result(player_name, score, max_score, time_spent, answers, exam_questions, token):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO results (player_name, score, max_score, time_spent, answers, exam_questions, token, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        player_name,
        score,
        max_score,
        time_spent,
        json.dumps(answers, ensure_ascii=False),
        json.dumps(exam_questions, ensure_ascii=False),
        token,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def get_all_results():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT player_name, score, max_score, time_spent, token, created_at FROM results ORDER BY created_at")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "player_name": r[0],
            "score": r[1],
            "max_score": r[2],
            "time_spent": r[3],
            "token": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]


def get_result_by_token(token):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT player_name, score, max_score, time_spent, answers, exam_questions, created_at FROM results WHERE token = ?", (token,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "player_name": row[0],
            "score": row[1],
            "max_score": row[2],
            "time_spent": row[3],
            "answers": json.loads(row[4]),
            "exam_questions": json.loads(row[5]),
            "created_at": row[6],
        }
    return None


def has_any_result():
    """检查是否已有考试记录（用于锁死容器）"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM results")
    count = c.fetchone()[0]
    conn.close()
    return count > 0
