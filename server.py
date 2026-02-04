from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from db import init_db, get_connection



OWNER_USER_ID = 1  
DATA_DIR = "dataset"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)


class TypingSession(BaseModel):
    user_id: int
    sequence: list
    text_typed: str

@app.post("/submit")
def submit(data: TypingSession):
    session_id = str(uuid.uuid4())
    label = 1 if data.user_id == OWNER_USER_ID else 0

    payload = {
        "user_id": data.user_id,
        "session_id": session_id,
        "sequence": data.sequence,
        "label": label,
        "text_typed": data.text_typed
    }

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO typing_sessions (user_id, session_id, label, data_json)
        VALUES (?, ?, ?, ?)
        """,
        (
            data.user_id,
            session_id,
            label,
            json.dumps(payload)
        )
    )

    conn.commit()
    conn.close()

    return {
        "status": "saved",
        "session_id": session_id,
        "label": label
    }

@app.get("/sessions")
def get_sessions(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT data_json FROM typing_sessions ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [json.loads(row[0]) for row in rows]
