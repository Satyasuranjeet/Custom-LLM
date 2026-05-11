from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Tiny model (FAST + small)
generator = pipeline(
    "text-generation",
    model="sshleifer/tiny-gpt2",  # VERY SMALL (~100MB)
    max_length=100
)

class Query(BaseModel):
    message: str

@app.post("/chat")
def chat(q: Query):
    response = generator(q.message)
    return {"response": response[0]["generated_text"]}


@app.get("/")
def root():
    return {"status": "LLM API running"}
