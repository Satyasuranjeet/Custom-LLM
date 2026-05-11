from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
import uvicorn

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

API_KEY = os.getenv("API_KEY")

class Query(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "✅ LLM API running with CORS"}

@app.post("/chat")
def chat(q: Query):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Missing API_KEY. Set it in server/.env")

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful and concise assistant.",
                    },
                    {
                        "role": "user",
                        "content": q.message,
                    },
                ],
                "temperature": 0.3,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"]}
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Unexpected response format from upstream API") from exc


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000a"))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
