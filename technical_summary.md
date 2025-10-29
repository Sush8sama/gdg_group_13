# ING Voice Assistant Hackathon 2025 – Technical Summary

## Problem Statement

Customers often face difficulties navigating banking services, accessing product information, and performing account-related requests efficiently. ING Belgium seeks an innovative, voice-enabled assistant that can provide natural, context-aware guidance in multiple languages (Dutch required, French and English optional) while securely handling customer data and transactions.

## Solution Architecture

The solution follows a modular architecture:

1. **Voice Interface**
   - Users interact via voice through a web-based UI.
   - Speech-to-text conversion is handled using Google’s API.
2. **Information Retrieval & AI Backend**

   - The transcribed query is passed to a Retrieval-Augmented Generation (RAG) LLM.
   - RAG model retrieves relevant information from:
     - Synthetic customer and transaction data (CSV files)
     - Website content chunks (NL, FR, EN)
   - LLM generates context-aware responses.

3. **Response Delivery**

   - Answer returned to the UI as text.
   - Optional text-to-speech integration possible for fully voice-enabled feedback.

4. **Data Security**
   - Sensitive customer data is securely processed.
   - Authentication and privacy mechanisms follow banking compliance standards.

## AI Implementation Details

- **Speech-to-Text:** Google Cloud Speech API converts voice input to text.
- **Retrieval-Augmented Generation (RAG):**
  - Embeddings created from customer data and website content.
  - Semantic search retrieves relevant chunks for each query.
  - LLM generates accurate, context-aware responses using retrieved context.
- **Multi-language Support:** Focus on Dutch; optional support for French and English.
- **Scalability & Performance:** Designed to handle multiple simultaneous user requests with low latency.

## Known Limitations

- Current prototype only supports Dutch reliably.
- Accuracy depends on the quality of synthetic data and coverage of website content.
- RAG LLM may provide incorrect answers if query context is ambiguous or missing.
- Voice interface relies on internet connectivity and Google API availability.
- No real-time transaction execution; responses are informational only.
