import os
import sqlite3
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is required. Add it to your .env file.")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is required. Add it to your .env file.")

client = OpenAI(api_key=api_key)
DATABASE = os.path.join("database", "airi.db")

limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["100 per hour"])


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    os.makedirs("database", exist_ok=True)
    connection = get_db()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


def get_or_create_session_id():
    if "session_id" not in session:
        session["session_id"] = os.urandom(16).hex()
    return session["session_id"]


def get_history(session_id):
    connection = get_db()
    rows = connection.execute("""
        SELECT role, message
        FROM conversations
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,)).fetchall()
    connection.close()
    return [{"role": row["role"], "message": row["message"]} for row in rows]


def save_message(session_id, role, message):
    connection = get_db()
    connection.execute("""
        INSERT INTO conversations (session_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, message, datetime.now(timezone.utc).isoformat()))
    connection.commit()
    connection.close()


@app.route("/")
def home():
    get_or_create_session_id()
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request."}), 400

    user_message = str(data.get("message", "")).strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(user_message) > 4000:
        return jsonify({"error": "Message is too long. Maximum 4000 characters."}), 400

    session_id = get_or_create_session_id()
    save_message(session_id, "user", user_message)

    try:
        history = get_history(session_id)
        conversation = [
            {"role": item["role"], "content": item["message"]}
            for item in history
        ]

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
            instructions=(
                "You are AIRI, an Artificial Intelligence Response Interface. "
                "Provide helpful, accurate and safe responses. Explain technical "
                "concepts clearly. Do not claim to have performed actions you did not perform. "
                "If uncertain, say so."
            ),
            input=conversation,
        )

        ai_response = response.output_text.strip()
        if not ai_response:
            ai_response = "I could not generate a response. Please try again."

        save_message(session_id, "assistant", ai_response)
        return jsonify({"response": ai_response})

    except Exception as error:
        app.logger.exception("AI request failed: %s", error)
        return jsonify({"error": "Unable to generate an AI response."}), 500


@app.route("/api/history")
def history():
    session_id = session.get("session_id")
    if not session_id:
        return jsonify([])
    return jsonify(get_history(session_id))


@app.route("/api/clear", methods=["POST"])
def clear():
    session_id = session.get("session_id")
    if session_id:
        connection = get_db()
        connection.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        connection.commit()
        connection.close()
    return jsonify({"success": True})


if __name__ == "__main__":
    initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=True)
