import Papa from "papaparse";
import { useEffect, useState } from "react";
import VoiceChat from "./components/VoiceChat";
import "./styles/App.css";

interface Customer {
  customer_id: string;
  name: string;
  birthdate: string;
  email: string;
  phone: string;
  address: string;
  segment_code: string;
}

export interface AudioResponse {
  result: string;
  transcript: string;
}

export interface RAGResponse {
  answer: string;
}

function App() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  useEffect(() => {
    fetch("/data/customers.csv")
      .then((res) => res.text())
      .then((csvText) => {
        const results = Papa.parse<Customer>(csvText, {
          header: true,
          skipEmptyLines: true,
          transformHeader: (header) => header.trim(),
          transform: (value) => value.trim(),
        });

        const filteredData = results.data.filter((c) => c.customer_id);
        setCustomers(filteredData);

      })
      .catch((err) => console.error("Failed to load customers CSV:", err));
  }, []);

  const handleSendRecording = async (audioBlob: Blob): Promise<AudioResponse> => {
    const formData = new FormData();
    formData.append("file", audioBlob, `recording_${Date.now()}.wav`);
    formData.append("language_code", "nl-BE");
    formData.append("user", selectedCustomer ? selectedCustomer.customer_id : "");

    const response = await fetch("http://localhost:8000/incomingAudio", {
      method: "POST",
      body: formData,
      // Remove Content-Type header - browser sets it automatically with boundary
    });

    // if (!response.ok) throw new Error("Upload failed");

    const data: AudioResponse = await response.json();


    // console.log("Assistant response:", data);
    return data; // return assistant response
  };

  const handleGetRAGResponse = async (text: string): Promise<RAGResponse> => {
    const body = JSON.stringify({
      text,
      user: selectedCustomer ? selectedCustomer.customer_id : "",
    });

    const response = await fetch("http://localhost:8000/rag", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    const data: RAGResponse = await response.json();
    return data;
  };

  return (
    <div className="app-wrapper">
      {/* Top-right optional user selection */}
      <div className="user-select-container">
        <select
          value={selectedCustomer?.customer_id || ""}
          onChange={(e) =>
            setSelectedCustomer(
              customers.find((c) => c.customer_id === e.target.value) || null
            )
          }
        >
          <option value="">Select your name (optional)</option>
          {customers.map((customer) => (
            <option key={customer.customer_id} value={customer.customer_id}>
              {customer.name}
            </option>
          ))}
        </select>
      </div>

      <div className="app-container">
        <div className="chat-card">
          <img src="src/assets/ing.png" alt="ING Logo" className="chat-logo" />
          <h1 className="chat-title">
            ING Voice Assistant
            {selectedCustomer ? ` - Hello, ${selectedCustomer.name}!` : ""}
          </h1>
          <p className="chat-subtitle">
            {selectedCustomer
              ? `Welcome back, ${selectedCustomer.name}! Tap below to speak with your assistant.`
              : "Tap the button below to start speaking with your digital assistant."}
          </p>

          <VoiceChat 
            onSendRecording={handleSendRecording}
            onGetRAGAnswer={handleGetRAGResponse}
          />
        </div>
      </div>

      <footer className="footer">© 2025 ING Voice Assistant Prototype</footer>
    </div>
  );
}

export default App;
