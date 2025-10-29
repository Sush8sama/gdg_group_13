import VoiceChat from "./components/VoiceChat";
import "./styles/App.css";

function App() {
  const handleSendRecording = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append("file", audioBlob, `recording_${Date.now()}.wav`);
    formData.append("language_code", "nl-BE");
    formData.append("user", "user-id-123");

    const response = await fetch("http://localhost:8000/incomingAudio", {
      method: "POST",
      body: formData,
      // Remove Content-Type header - browser sets it automatically with boundary
    });

    if (!response.ok) throw new Error("Upload failed");

    const data = await response.json();


    // console.log("Assistant response:", data);
    return data.answer; // return assistant response
  };

  return (
    <div className="app-wrapper">
      <div className="app-container">
        <div className="chat-card">
          <img src="src/assets/ing.png" alt="ING Logo" className="chat-logo" />
          <h1 className="chat-title">ING Voice Assistant</h1>
          <p className="chat-subtitle">
            Tap the button below to start speaking with your digital assistant.
          </p>
          <VoiceChat onSendRecording={handleSendRecording} />
        </div>
      </div>

      <footer className="footer">© 2025 ING Voice Assistant Prototype</footer>
    </div>
  );
}

export default App;
