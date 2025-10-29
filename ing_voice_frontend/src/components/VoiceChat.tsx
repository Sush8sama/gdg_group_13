import { Mic, StopCircle, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface VoiceChatProps {
  onSendRecording: (audioBlob: Blob) => Promise<string>;
  // prompt: (string: string) => Promise<string>;
}

const VoiceChat: React.FC<VoiceChatProps> = ({ onSendRecording   }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [conversation, setConversation] = useState<
    { type: "user" | "assistant"; text: string }[]
  >([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });

        setConversation((prev) => [
          ...prev,
          { type: "user", text: "🎤 Sending voice message..." },
        ]);

        try {
          const assistantText = await onSendRecording(audioBlob);
          setConversation((prev) => [...prev, { type: "assistant", text: assistantText }]);
        } catch {
          setConversation((prev) => [
            ...prev,
            { type: "assistant", text: "❌ Failed to get assistant response." },
          ]);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error(err);
      setConversation((prev) => [
        ...prev,
        { type: "assistant", text: "❌ Could not access microphone." },
      ]);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  const cancelRecording = () => {
    // Prevent sending when canceled
    setIsRecording(false);
    audioChunksRef.current = [];

    // Temporarily remove the onstop handler
    if (mediaRecorderRef.current) {
        mediaRecorderRef.current.onstop = null;
        mediaRecorderRef.current.stop();
    }
    };

  return (
    <div className="voice-chat-container">
      <div className="conversation">
        {conversation.map((msg, idx) => (
          <div key={idx} className={`message ${msg.type}`}>
            {msg.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="controls">
        {!isRecording ? (
          <button className="record-btn start" onClick={startRecording}>
            <Mic size={22} /> Start Recording
          </button>
        ) : (
          <>
            <button className="record-btn stop" onClick={stopRecording}>
              <StopCircle size={22} /> Stop & Send
            </button>
            <button className="record-btn cancel" onClick={cancelRecording}>
              <X size={22} /> Cancel
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default VoiceChat;
