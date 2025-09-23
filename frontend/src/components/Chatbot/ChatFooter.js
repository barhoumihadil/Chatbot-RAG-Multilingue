import React, { useState } from "react";
import EmojiPicker from "./EmojiPicker";
import { useNavigate } from "react-router-dom";

export default function ChatFooter({ sendMessage }) {
  const [input, setInput] = useState("");
  const [file, setFile] = useState(null);
  const [showEmoji, setShowEmoji] = useState(false);
  const [listening, setListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const navigate = useNavigate(); // 🔹 pour rediriger vers ResumePage

  const handleSend = () => {
    if (!input.trim() && !file) return;
    sendMessage({ text: input, file });
    setInput("");
    setFile(null);
    stopListening();
  };

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const startListening = () => {
    if (!("webkitSpeechRecognition" in window)) return alert("Navigateur non supporté");

    const rec = new window.webkitSpeechRecognition();
    rec.lang = "fr-FR";
    rec.interimResults = true;
    rec.continuous = true;

    rec.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setInput(transcript);
    };

    rec.onerror = (event) => {
      console.error("Erreur reconnaissance vocale :", event.error);
      stopListening();
    };

    rec.onend = () => setListening(false);

    rec.start();
    setRecognition(rec);
    setListening(true);
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
      setListening(false);
    }
  };

  const addEmoji = (emoji) => setInput(input + emoji);

  return (
    <div className="chatgpt-footer">
      {file && (
        <div className="file-preview">
          {file.type.startsWith("image") && <img src={URL.createObjectURL(file)} alt="preview" />}
          <span>{file.name}</span>
          <button onClick={() => setFile(null)}>❌</button>
        </div>
      )}

      <input
        type="text"
        placeholder="Écris ton message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />

      {/* Micro */}
      <button onClick={listening ? stopListening : startListening}>
        {listening ? "🎙️ Arrêter" : "🎤 Parler"}
      </button>

      {/* Envoyer & Supprimer */}
      {input && (
        <>
          <button onClick={handleSend}>✔️ Envoyer</button>
          <button onClick={() => setInput("")}>❌ Supprimer</button>
        </>
      )}

      {/* Upload */}
      <label className="file-upload-btn">
        📎
        <input type="file" onChange={handleFileChange} />
      </label>

      {/* Emoji */}
      <button onClick={() => setShowEmoji(!showEmoji)}>😊</button>
      {showEmoji && <EmojiPicker addEmoji={addEmoji} />}

      {/* 🚀 Résumer */}
      <button
        onClick={() => navigate("/resume")}
        className="resume-btn"
      >
        📄 Résumer
      </button>
    </div>
  );
}
