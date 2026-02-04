from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import json
import os
from fastapi.middleware.cors import CORSMiddleware


OWNER_USER_ID = 1  # <-- YOU
DATA_DIR = "dataset"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()

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
def submit_session(data: TypingSession):
    session_id = str(uuid.uuid4())

    label = 1 if data.user_id == OWNER_USER_ID else 0

    payload = {
        "user_id": data.user_id,
        "session_id": session_id,
        "sequence": data.sequence,
        "label": label,
        "text_typed": data.text_typed
    }

    filename = f"{DATA_DIR}/session_user{data.user_id}_{session_id}.json"
    with open(filename, "w") as f:
        json.dump(payload, f, indent=2)

    return {"status": "saved", "label": label}
