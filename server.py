from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import uuid
import os

# ---------- CONFIG ----------
OWNER_USER_ID = 1  # YOU = label 1, others = 0

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- SCHEMA ----------
class TypingSession(BaseModel):
    user_id: int
    sequence: list
    text_typed: str

# ---------- API ----------
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

    supabase.table("typing_sessions").insert({
        "user_id": data.user_id,
        "session_id": session_id,
        "label": label,
        "data": payload
    }).execute()

    return {
        "status": "saved",
        "session_id": session_id,
        "label": label
    }
