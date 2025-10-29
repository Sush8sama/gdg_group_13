import { Mic, StopCircle, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { AudioResponse, RAGResponse } from "../App";

interface VoiceChatProps {
  onSendRecording: (audioBlob: Blob) => Promise<AudioResponse>;
  onGetRAGAnswer: (text: string) => Promise<RAGResponse>
}

interface ConversationMessage {
  type: "user" | "assistant" | "placeholder";
  text: string;
}

const VoiceChat: React.FC<VoiceChatProps> = ({ onSendRecording, onGetRAGAnswer }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

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

        // User placeholder
        const userPlaceholderIndex = conversation.length;
        setConversation((prev) => [
          ...prev,
          { type: "placeholder", text: "🎤 Transcribing..." },
        ]);

        try {
          const data = await onSendRecording(audioBlob);

          // Replace placeholder with transcription
          setConversation((prev) => {
            const newConv = [...prev];
            newConv[userPlaceholderIndex] = { type: "user", text: data.transcript };
            return newConv;
          });

          // Assistant placeholder
          const assistantPlaceholderIndex = conversation.length + 1;
          setConversation((prev) => [
            ...prev,
            { type: "placeholder", text: "🎤 Assistant is thinking ..." },
          ]);

          try {
            const answer = await onGetRAGAnswer(data.transcript)
            
            // Replace assistant placeholder with actual response
            setConversation((prev) => {
              const newConv = [...prev];
              newConv[assistantPlaceholderIndex] = { type: "assistant", text: answer.answer };
              return newConv;
            });
          } catch {
            setConversation((prev) => {
            const newConv = [...prev];
            newConv[assistantPlaceholderIndex] = {
              type: "assistant",
              text: "❌ Failed to get answer.",
            };
            return newConv;
          });
          }

        } catch {
          setConversation((prev) => {
            const newConv = [...prev];
            newConv[userPlaceholderIndex] = {
              type: "assistant",
              text: "❌ Failed to get transcription.",
            };
            return newConv;
          });
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
    setIsRecording(false);
    audioChunksRef.current = [];
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.onstop = null;
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="voice-chat-container">
      <div className="conversation">
        {conversation.map((msg, idx) => (
          <div
            key={idx}
            className={`message ${msg.type}`}
            style={{
              display: "flex",
              justifyContent: msg.type === "placeholder" ? "center" : undefined,
            }}
          >
            {msg.type === "user" && <Mic size={16} style={{ marginRight: 6 }} />}
            <span
              className={msg.type === "placeholder" ? "placeholder-text" : undefined}
            >
              {msg.text}
            </span>
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
