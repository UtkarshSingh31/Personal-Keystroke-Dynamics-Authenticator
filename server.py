from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import uuid
import os

# ---------- CONFIG ----------
OWNER_USER_ID = 1  # YOU

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- APP ----------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow local HTML
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- SCHEMA ----------
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

    try:
        result = supabase.table("typing_sessions").insert({
            "user_id": data.user_id,
            "session_id": session_id,
            "label": label,
            "data": payload
        }).execute()

        # If something is really wrong, data will be None
        if result.data is None:
            raise RuntimeError("Insert failed with no data returned")

        return {
            "status": "saved",
            "session_id": session_id,
            "label": label
        }

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/download")
def download_dataset():
    result = supabase.table("typing_sessions").select("*").execute()

    if result.data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch data")

    return result.data
