from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.websockets import router as websockets_router

app = FastAPI(title="DynamoAuth Realtime Detection")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(websockets_router)

@app.get("/")
def root():
    return {"status": "DynamoAuth Backend Running"}
