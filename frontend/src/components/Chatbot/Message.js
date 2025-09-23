import React from "react";
import FilePreview from "./FilePreview";

export default function Message({ sender, text, file }) {
  return (
    <div className={`chatgpt-message ${sender}`}>
      {text}
      {file && <FilePreview file={file} />}
    </div>
  );
}
