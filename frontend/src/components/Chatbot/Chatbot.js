import React, { useState, useRef, useEffect } from "react";
import ChatHeader from "./ChatHeader";
import ChatBody from "./ChatBody";
import ChatFooter from "./ChatFooter";
import TypingIndicator from "./TypingIndicator";
import CompanySearch from "./CompanySearch";
import "./Chatbot.css";
import { useNavigate } from "react-router-dom";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const [showHistory, setShowHistory] = useState(true);
  const chatEndRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async (message) => {
    let text = "";
    let file = null;

    if (typeof message === "string") {
      text = message;
    } else if (typeof message === "object") {
      text = message.text || "";
      file = message.file || null;
    }

    if (!text.trim() && !file) return;

    setMessages((prev) => [...prev, { sender: "user", text, file }]);
    setTyping(true);

    try {
      const payload = { message: text };

      if (file) {
        const reader = new FileReader();
        reader.onloadend = async () => {
          payload.file = { data: reader.result };
          const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const data = await response.json();
          setMessages((prev) => [...prev, { sender: "bot", text: data.response }]);
          setTyping(false);
          scrollToBottom();
        };
        reader.readAsDataURL(file);
        return;
      }

      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { sender: "bot", text: data.response }]);
    } catch (err) {
      setMessages((prev) => [...prev, { sender: "bot", text: "⚠️ Erreur serveur" }]);
    } finally {
      setTyping(false);
      scrollToBottom();
    }
  };

  const newChat = () => setMessages([]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing]);

  return (
    <div className="chatgpt-container">
      {showHistory && (
        <div className="history-sidebar">
          <h3>Historique</h3>
          {messages.map((msg, i) => (
            <div key={i} className={`history-message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
          <button className="new-chat-btn" onClick={newChat}>
            ➕ Nouveau Chat
          </button>
        </div>
      )}

      <div className="chat-wrapper">
        <ChatHeader 
          showHistory={showHistory} 
          setShowHistory={setShowHistory} 
          sendMessage={sendMessage} 
        />

        <ChatBody messages={messages} chatEndRef={chatEndRef} />
        {typing && <TypingIndicator />}

        {/* Bouton Résumer → redirection vers /resume */}
        <div className="chat-footer-buttons">
          <ChatFooter sendMessage={sendMessage} />
          
        </div>
      </div>
    </div>
  );
}
