import mysql.connector
from contextlib import contextmanager
from config.settings import MYSQL_CONFIG
import json
from typing import Dict, Any, Optional
from datetime import date
import uuid

@contextmanager
def get_db():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def create_session(session_id: str, topic: str, user_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO session_logs (
                session_id, started_at, completed, topic, user_id
            )
            VALUES (%s, NOW(), 0, %s, %s)
            """,
            (session_id, topic, user_id)
        )
        conn.commit()

def mark_session_completed(session_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE session_logs
            SET completed = 1, completed_at = NOW()
            WHERE session_id = %s
            """,
            (session_id,)
        )
        conn.commit()

def get_current_question(session_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT topic, question, bloom_level, is_answered
            FROM questions
            WHERE session_id = %s AND is_answered = 0
            ORDER BY bloom_level ASC LIMIT 1
            """,
            (session_id,)
        )
        return cursor.fetchone()

def save_question(session_id: str, topic: str, question: str, bloom_level: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (session_id, topic, question, bloom_level, is_answered)
            VALUES (%s, %s, %s, %s, 0)
            """,
            (session_id, topic, question, bloom_level)
        )
        conn.commit()

def mark_answered(session_id: str, bloom_level: int, user_answer: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE questions
            SET is_answered = 1, user_answer = %s
            WHERE session_id = %s AND bloom_level = %s
            """,
            (user_answer, session_id, bloom_level)
        )
        conn.commit()

def get_daily_topic() -> Optional[Dict[str, Any]]:
    today = str(date.today())
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT topic, topic_prompt
            FROM daily_topic
            WHERE topic_date = %s
            """,
            (today,)
        )
        return cursor.fetchone()

def get_session_summary(session_id: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                q.bloom_level,
                q.question,
                q.user_answer
            FROM questions q
            WHERE q.session_id = %s
            ORDER BY q.bloom_level ASC
            """,
            (session_id,)
        )
        questions = cursor.fetchall()
        
        return {
            "total_questions": len(questions),
            "completed_levels": [q["bloom_level"] for q in questions],
            "questions_and_answers": questions
        }

def get_session_topic(session_id: str) -> Optional[str]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT topic FROM session_logs WHERE session_id = %s",
            (session_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def save_report(session_id: str, user_id: str, topic: str, report: Dict[str, Any]) -> str:
    with get_db() as conn:
        cursor = conn.cursor()
        report_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO reports (
                report_id,
                session_id,
                user_id,
                topic,
                summary,
                strengths,
                weaknesses,
                suggestions,
                revised_suggestion,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                report_id,
                session_id,
                user_id,
                topic,
                report["summary"],
                json.dumps(report["strengths"], ensure_ascii=False),
                json.dumps(report["weaknesses"], ensure_ascii=False),
                json.dumps(report["suggestions"], ensure_ascii=False),
                report["revised_suggestion"]
            )
        )
        conn.commit()
        return report_id

def get_saved_report(session_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                report_id,
                session_id,
                user_id,
                topic,
                summary,
                strengths,
                weaknesses,
                suggestions,
                revised_suggestion,
                created_at
            FROM reports 
            WHERE session_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (session_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return {
                "report_id": result[0],
                "session_id": result[1],
                "user_id": result[2],
                "topic": result[3],
                "summary": result[4],
                "strengths": json.loads(result[5]),
                "weaknesses": json.loads(result[6]),
                "suggestions": json.loads(result[7]),
                "revised_suggestion": result[8],
                "created_at": result[9].isoformat()
            }
        return None 