import React from "react";
import Message from "./Message";

export default function ChatBody({ messages, chatEndRef }) {
  return (
    <div className="chatgpt-body">
      {messages.map((msg, i) => (
        <Message key={i} sender={msg.sender} text={msg.text} file={msg.file} />
      ))}
      <div ref={chatEndRef} />
    </div>
  );
}
