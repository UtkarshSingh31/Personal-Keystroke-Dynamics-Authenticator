from fastapi import FastAPI, HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import uuid
import os
import math
from dotenv import load_dotenv
import asyncio

# ---------- CONFIG ----------
OWNER_USER_ID = 11  # owner/user 11
TOTAL_USERS = 15
TOTAL_SESSIONS = 8
MIN_WORDS = 50
MIN_EVENTS = 200

load_dotenv() 

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TypingSession(BaseModel):
    user_id: int
    sequence: list
    text_typed: str
    word_count: int
    session_number: int

@app.get("/")
def root():
    return {"status": "ok"}

def insert_to_supabase(row):
    return supabase.table("typing_sessions").insert(row).execute()

@app.post("/submit")
async def submit(request:Request):
    try: 
        data = await request.json()
        user_id = data.get("user_id")
        sequence = data.get("sequence", [])
        text_typed = data.get("text_typed", "")
        if not isinstance(text_typed, str):
            raise ValueError("text_typed must be a string")
        word_count = len(text_typed.split())
        session_number = data.get("session_number")

        if not isinstance(user_id, int) or not 1 <= user_id <= TOTAL_USERS:
            raise ValueError(f"user_id must be an integer from 1 to {TOTAL_USERS}")
        if not isinstance(sequence, list) or len(sequence) < MIN_EVENTS:
            raise ValueError(f"At least {MIN_EVENTS} keystroke events are required")
        if word_count < MIN_WORDS:
            raise ValueError(f"At least {MIN_WORDS} words are required")
        if not isinstance(session_number, int) or not 1 <= session_number <= TOTAL_SESSIONS:
            raise ValueError(f"session_number must be from 1 to {TOTAL_SESSIONS}")

        for event in sequence:
            hold_time = event.get("hold_time")
            flight_time = event.get("flight_time")
            if (not isinstance(hold_time, (int, float)) or
                    not math.isfinite(hold_time) or hold_time <= 0):
                raise ValueError("Every hold_time must be greater than zero")
            if (not isinstance(flight_time, (int, float)) or
                    not math.isfinite(flight_time) or flight_time < 0):
                raise ValueError("Every flight_time must be non-negative")

        session_id = str(uuid.uuid4())
        label = 1 if user_id == OWNER_USER_ID else 0
    
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "sequence": sequence,
            "label": label,
            "text_typed": text_typed,
            "word_count": word_count,
            "session_number": session_number
        }

        result = await asyncio.to_thread(
            insert_to_supabase,
            {
                "user_id":user_id,
                "session_id": session_id,
                "label": label,
                "data": payload
            }
        )

        if not result.data :
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


