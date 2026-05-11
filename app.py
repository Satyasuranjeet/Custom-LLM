from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import uvicorn
from groq import Groq

# Load environment variables from server/.env regardless of current working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

# ✅ CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

class Query(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "✅ LLM API running with CORS"}

@app.post("/chat")
def chat(q: Query):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY (or API_KEY). Set it in server/.env")

    try:
        client = Groq(api_key=API_KEY)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and concise assistant.",
                },
                {
                    "role": "user",
                    "content": q.message,
                },
            ],
            temperature=0.3,
        )
        return {"response": completion.choices[0].message.content}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
