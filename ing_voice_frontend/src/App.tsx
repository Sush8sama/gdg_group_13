import Papa from "papaparse";
import { useEffect, useState } from "react";
import VoiceChat from "./components/VoiceChat";
import "./styles/App.css";
import type { Language } from "./translations";
import translations from "./translations";

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
  const [language, setLanguage] = useState<Language>("nl-BE");
  
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
    formData.append("language_code", language);
    formData.append("user", selectedCustomer ? selectedCustomer.customer_id : "");

    const response = await fetch("http://localhost:8000/incomingAudio", {
      method: "POST",
      body: formData,
    });

    const data: AudioResponse = await response.json();
    return data;
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
      {/* Top-right optional user & language selection */}
      <div className="user-select-container">
        <select
          value={language}
          onChange={(e) =>
            setLanguage(e.target.value as "en-US" | "nl-BE" | "fr-FR")
          }
        >
          <option value="nl-BE">🇳🇱 Dutch</option>
          <option value="en-US">🇬🇧 English</option>
          <option value="fr-FR">🇫🇷 French</option>
        </select>

        <select
          value={selectedCustomer?.customer_id || ""}
          onChange={(e) =>
            setSelectedCustomer(
              customers.find((c) => c.customer_id === e.target.value) || null
            )
          }
        >
          <option value="">{translations[language].selectUser}</option>
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
            {translations[language].title}
            {selectedCustomer
              ? ` - ${translations[language].greeting}, ${selectedCustomer.name}!`
              : ""}
          </h1>
          <p className="chat-subtitle">
            {selectedCustomer
              ? translations[language].welcomeBack(selectedCustomer.name)
              : translations[language].welcome}
          </p>

          <VoiceChat
            onSendRecording={handleSendRecording}
            onGetRAGAnswer={handleGetRAGResponse}
            language={language}
            // Use customer ID as key so chat resets on user change
            key={selectedCustomer?.customer_id || "default-user"}
          />
        </div>
      </div>

      <footer className="footer">{translations[language].footer}</footer>
    </div>
  );
}

export default App;
