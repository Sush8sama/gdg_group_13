# main.py
import os
import base64
import re

import vertexai
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import speech
from pydantic import BaseModel
from src.rag import rag_func
from vertexai.generative_models import GenerativeModel
from google.cloud import texttospeech

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- allow all origins
    allow_credentials=False,  # must be False if allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ID = os.getenv("PROJECT_ID", "texttospeeach-476609")
LOCATION = os.getenv(
    "LOCATION", "europe-west3"
)  # pick a region where the model is available

# initialize once at startup
vertexai.init(project=PROJECT_ID, location=LOCATION)

# choose the model you want; e.g. "gemini-2.5-flash" or another available model in your region
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class TextPayload(BaseModel):
    text: str
    user: str
    language: str


@app.get("/")
def read_root():
    return {"message": "Hello, Backend!"}


@app.post("/gemini")
def gemini_prompt(payload: TextPayload):
    print(f"Received payload: {payload}")
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


@app.post("/rag")
def rag_endpoint(prompt: TextPayload):
    try:
        # Get the answer from your RAG function
        ans = rag_func(prompt.text, prompt.user)
        answer_text = ans.text if hasattr(ans, "text") else str(ans)

        cleaned_answer = re.sub(
            r"\b(star|stars)\b", "", answer_text, flags=re.IGNORECASE
        )
        cleaned_answer = re.sub(r"\*+", "", cleaned_answer)  # remove literal asterisks
        cleaned_answer = re.sub(
            r"\s{2,}", " ", cleaned_answer
        ).strip()  # tidy up spaces

        # --- Generate TTS using premium nl-BE voice ---
        tts_client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=cleaned_answer)

        # Language/voice mapping
        language_map = {
            "en-GB": {
                "language_code": "en-GB",
                "voice_name": "en-GB-Chirp3-HD-Iapetus",
            },
            "en-US": {
                "language_code": "en-US",
                "voice_name": "en-US-Chirp3-HD-Iapetus",
            },
            "nl-BE": {
                "language_code": "nl-BE",
                "voice_name": "nl-BE-Chirp3-HD-Vindemiatrix",
            },
            "fr-FR": {
                "language_code": "fr-FR",
                "voice_name": "fr-FR-Chirp3-HD-Lyra",
            },
        }

        # Default to en-GB if language not found
        lang_info = language_map.get(prompt.language, language_map["en-GB"])

        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_info["language_code"],
            name=lang_info["voice_name"],
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # Convert audio bytes to base64 so frontend can play it
        audio_base64 = base64.b64encode(tts_response.audio_content).decode("utf-8")

        # Return both the text and audio
        return {"answer": answer_text, "audio_base64": audio_base64}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vertex AI error: {str(e)}")


@app.post("/incomingAudio")
async def process_audio(
    file: UploadFile = File(...), language_code: str = Form(...), user: str = Form(...)
):
    if not file:
        raise HTTPException(status_code=400, detail="Audio file is required.")

    # Placeholder for audio processing logic
    try:
        # Use European regional endpoint for better latency
        client_options = {"api_endpoint": "eu-speech.googleapis.com"}
        client = speech.SpeechClient(client_options=client_options)

        # Read the audio file content directly from the uploaded file
        content = await file.read()

        audio = speech.RecognitionAudio(content=content)

        # Use OGG_OPUS encoding for webm/opus audio from browser MediaRecorder
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,  # Standard sample rate for browser MediaRecorder with OPUS
            audio_channel_count=1,  # Browser MediaRecorder typically records in stereo (2 channels)
            language_code=language_code,
        )

        response = client.recognize(config=config, audio=audio)
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
            # print("Transcript: {}".format(result.alternatives[0].transcript))

        processed_result = (
            f"Processed audio for user {user} in language {language_code}"
        )

        return {
            "result": processed_result,
            "transcript": transcript,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Audio processing error: {str(e)}")
