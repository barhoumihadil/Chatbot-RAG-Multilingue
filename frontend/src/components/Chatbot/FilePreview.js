import React from "react";

export default function FilePreview({ file }) {
  return (
    <div className="file-preview">
      {file.type.startsWith("image") && <img src={URL.createObjectURL(file)} alt="preview" />}
      <span>{file.name}</span>
    </div>
  );
}
