from fastapi import FastAPI, HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import uuid
import os
from dotenv import load_dotenv
import asyncio

# ---------- CONFIG ----------
OWNER_USER_ID = 1  # YOU

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

@app.get("/")
def root():
    return {"status": "ok"}

def insert_to_supabase(row):
    return supabase.table("typing_sessions").insert(row).execute()

@app.post("/submit")
async def submit(request:Request):
    try: 
        data = await request.json()
        session_id = str(uuid.uuid4())
        label = 1 if data.user_id == OWNER_USER_ID else 0
    
        payload = {
            "user_id": data['user_id'],
            "session_id": session_id,
            "sequence": data['sequence'],
            "label": label,
            "text_typed": data['text_typed']
        }

        result = await asyncio.to_thread(
            insert_to_supabase,
            {
                "user_id":data['user_id'],
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


