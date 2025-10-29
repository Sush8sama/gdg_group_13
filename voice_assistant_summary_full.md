# Voice-Enabled Banking Assistant — Technical Summary

## Goal

The project aims to develop a simple, low-latency voice-enabled banking assistant capable of transcribing speech, retrieving relevant knowledge using a Retrieval-Augmented Generation (RAG) approach, and generating responses through a Gemini language model.

---

## Architecture Overview

### Frontend

The frontend, called **ing_voice_frontend**, is built with **React (Vite)** and centers on a `VoiceChat` component. This interface allows users to record their voice through `getUserMedia` and `MediaRecorder`, producing an audio Blob that is sent to the backend endpoint `/incomingAudio`. Once transcription is received, the frontend calls the `/rag` endpoint to generate an answer. A simple customer selector, populated from a CSV file, tags each request with a `customer_id` for contextual responses.

### Backend

The **backend**, developed with **FastAPI**, exposes several endpoints with permissive CORS enabled. These include:
- `/` for health checks,  
- `/incomingAudio` to handle transcription via Google Cloud Speech-to-Text,  
- `/rag` to generate a RAG-based response using Vertex AI Gemini, and  
- `/gemini` for direct prompts to the Gemini model without retrieval.  

The backend relies on environment variables for authentication through a service account and intentionally omits traditional authentication to simplify prototype setup.

### AI Services

The system integrates multiple Google Cloud services. Speech is transcribed with **Google Cloud Speech-to-Text (EU endpoint)**, and text generation uses **Vertex AI** with the **Gemini model** enhanced by a RAG tool.

---

## Data Flow

The data flow begins when a user records an audio message. The frontend sends a `FormData` payload—containing the audio file, language code, and user identifier—to the `/incomingAudio` endpoint. The backend transcribes this audio using Google’s Speech-to-Text API and returns the transcript. The frontend then calls `/rag`, sending the transcript and user ID. The backend constructs a retrieval-augmented prompt for Gemini, which produces a grounded, context-aware answer that is returned to the user.

---

## Regions

To maintain EU data residency, different regional services are used:
- Vertex AI initialization for the backend occurs in `europe-west3`.
- The RAG module runs in `europe-west1`.
- The Speech API uses the endpoint `eu-speech.googleapis.com`.

---

## Problem Statement

The challenge is to provide a low-latency, EU-local voice assistant for banking scenarios. The system must capture and transcribe user speech, retrieve knowledge from internal corpora, and generate context-aware answers. It should support **Dutch (Belgium)** speech (`nl-BE`) and operate as a lightweight, hack-friendly prototype requiring minimal configuration.

---

## Solution Details

### Speech Recognition

Speech recognition uses Google Cloud Speech-to-Text in synchronous mode. Audio is encoded as `OGG_OPUS`, sampled at 48 kHz, and recorded in two channels. The language code is supplied by the client (defaulting to `nl-BE`). The backend concatenates all transcription results into a single text string.

### RAG Retrieval

The retrieval component automatically selects the most recently created corpus. The configuration retrieves up to five (`top_k = 5`) relevant documents within a vector distance threshold of 0.5. The Gemini model (`gemini-2.0-flash`) is attached using `Tool.from_retrieval`.

### LLM Generation

Two Gemini models are used. The `/gemini` endpoint employs the environment variable `GEMINI_MODEL`, defaulting to `gemini-2.5-flash`, while the RAG system uses `gemini-2.0-flash`. Prompts follow this structure:

```
ROLE: banking customer service chatbot
QUESTION: user transcript
CONTEXT: user_info hint (customer_id)
```

---

## Data Handling

Each frontend request includes a `customer_id` field representing the user. The backend never retrieves or processes personally identifiable information; this identifier serves only as a contextual hint. All data is processed and stored in EU regions to maintain compliance.

---

## Known Limitations

### Audio Encoding Mismatch

Browser `MediaRecorder` instances may output `webm/opus` files, whereas the backend expects `OGG_OPUS`. This can be mitigated by setting the client’s MIME type to `"audio/webm;codecs=opus"` and updating backend handling accordingly.

### Synchronous STT

The Speech-to-Text API operates synchronously, which can block requests and limit transcription length to about one minute. Streaming transcription is not yet implemented.

### Region Inconsistency

The backend and RAG modules run in different regions (`europe-west3` and `europe-west1`), introducing potential latency and compliance issues.

### RAG Corpus Selection

At present, the system always selects the last created corpus, with no configuration option to specify a fixed one.

### User Context

Personalization is minimal, relying only on the provided `customer_id` string.

### Model Version Mismatch

The `/gemini` endpoint and RAG module use different model versions (`gemini-2.5-flash` and `gemini-2.0-flash`), which may yield inconsistent results.

### Security

The prototype uses open CORS and lacks authentication or authorization, leaving it unsuitable for production deployment.

### Observability

Logging and error handling are minimal, often resulting in raw HTTP 500 errors when exceptions occur.

### Cost and Rate Control

The system has no built-in quota, caching, or cost-control mechanisms.

### Language Handling

Language is hard-coded to `nl-BE`, and there is no UI support or automatic detection for other languages.

### Privacy and Data Residency

Although the design assumes EU-local data handling, region mismatches (between west1 and west3) may challenge strict data residency expectations.

---

## Overall Summary

The prototype demonstrates a functioning, low-latency voice-enabled assistant for banking that operates within EU regions. It successfully combines real-time speech transcription, RAG-based retrieval, and Gemini-driven generation. Nonetheless, it can be improved through better audio encoding alignment, consistent regional configuration, stronger security measures, and enhanced observability.
