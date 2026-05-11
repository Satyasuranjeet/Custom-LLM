from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful and concise assistant."
                    },
                    {
                        "role": "user",
                        "content": q.message
                    }
                ],
                "temperature": 0.3
            }
        )

        data = response.json()

        return {
            "response": data["choices"][0]["message"]["content"]
        }

    except Exception as e:
        return {"error": str(e)}
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port
    )
