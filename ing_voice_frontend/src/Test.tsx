import React, { useRef, useState } from "react";

type GeminiResponse = { result?: string } | string;

export default function Test() {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function sendText(): Promise<void> {
    setError(null);
    setResponse(null);

    const text = textareaRef.current?.value ?? "";
    if (!text.trim()) {
      setError("Please enter some text before sending.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/rag", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json, text/plain",
        },
        // If you need cookies/auth, uncomment the next line and ensure server CORS allows credentials
        // credentials: "include",
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Server responded ${res.status}: ${body}`);
      }

      const contentType = res.headers.get("content-type") || "";
      let data: GeminiResponse;
      if (contentType.includes("application/json")) {
        data = await res.json();
      } else {
        data = await res.text();
      }

      if (typeof data === "string") {
        setResponse(data);
      } else if (data && (data as any).result) {
        setResponse((data as any).result);
      } else {
        setResponse(JSON.stringify(data));
      }
    } catch (err: any) {
      setError(err?.message ?? String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4 max-w-2xl">
      <label htmlFor="myTextarea" className="block mb-2 font-medium">
        Prompt
      </label>

      <textarea
        id="myTextarea"
        ref={textareaRef}
        rows={6}
        className="w-full p-2 border rounded"
        placeholder="Type your prompt here..."
      />

      <div className="mt-3 flex gap-2">
        <button
          onClick={sendText}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {loading ? "Sending…" : "Send"}
        </button>

        <button
          type="button"
          onClick={() => {
            if (textareaRef.current) textareaRef.current.value = "";
            setResponse(null);
            setError(null);
          }}
          className="px-3 py-2 border rounded"
        >
          Clear
        </button>
      </div>

      {error && <div className="mt-3 text-red-600">Error: {error}</div>}

      {response && (
        <div className="mt-3 p-3 bg-gray-100 rounded">
          <pre className="whitespace-pre-wrap">{response}</pre>
        </div>
      )}
    </div>
  );
}
