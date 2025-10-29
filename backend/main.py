# main.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # <-- allow all origins
    allow_credentials=False,  # must be False if allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ID = os.getenv("PROJECT_ID", "texttospeeach-476609")
LOCATION = os.getenv("LOCATION", "europe-west3")  # pick a region where the model is available

# initialize once at startup
vertexai.init(project=PROJECT_ID, location=LOCATION)

# choose the model you want; e.g. "gemini-2.5-flash" or another available model in your region
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class TextPayload(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Hello, Backend!"}

@app.post("/gemini")
def gemini_prompt(payload: TextPayload):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text payload is required.")

    try:
        model = GenerativeModel(MODEL_NAME)
        # generate_content returns a response object with .text
        response = model.generate_content(payload.text)
        return {"result": response.text}
    except Exception as e:
        # log the underlying error server-side
        # (in production, use structured logging and remove stack traces from responses)
        raise HTTPException(status_code=500, detail=f"Vertex AI error: {str(e)}")
