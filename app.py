from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import os
import uvicorn

app = FastAPI()

# Tiny model (FAST + small)
generator = pipeline(
    "text-generation",
    model="microsoft/phi-1_5"
)

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat(q: Query):
    response = generator(
        q.message,
        max_length=100,
        num_return_sequences=1
    )

    return {
        "response": response[0]["generated_text"]
    }

@app.get("/")
def root():
    return {"status": "LLM API running"}

# IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port
    )
