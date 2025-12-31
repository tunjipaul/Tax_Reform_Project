from fastapi import FastAPI
from app.api import chat

app = FastAPI(title="Nigeria Tax Q&A Assistant")

# Include chat routes
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Welcome to Nigeria Tax Q&A Assistant API"}
