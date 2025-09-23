import React, { useState } from "react";

export default function ResumePage() {
  const [text, setText] = useState("");
  const [file, setFile] = useState(null); // pour stocker le fichier PDF
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    if (!text.trim() && !file) return; // vérifier qu'il y a du texte ou un fichier
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("input_text", text);
      if (file) formData.append("file", file); // ajouter le fichier si présent

      const response = await fetch("http://localhost:8000/resumeur", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      console.error(err);
      setSummary("Erreur lors du résumé.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
    } else {
      alert("Veuillez sélectionner un fichier PDF.");
      e.target.value = null;
      setFile(null);
    }
  };

  const removeFile = () => setFile(null);

  return (
    <div style={{ padding: "20px", maxWidth: "800px", margin: "0 auto" }}>
      <h2>Résumé de texte / PDF</h2>

      <textarea
        rows={10}
        style={{ width: "100%", padding: "10px" }}
        placeholder="Collez votre texte ici..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div style={{ margin: "10px 0" }}>
        <label
          style={{
            display: "inline-block",
            padding: "8px 12px",
            background: "#343541",
            color: "white",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          📄 Choisir un PDF
          <input
            type="file"
            accept="application/pdf"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
        </label>
        {file && (
          <span style={{ marginLeft: "10px" }}>
            {file.name} <button onClick={removeFile}>❌</button>
          </span>
        )}
      </div>

      <button
        onClick={handleSummarize}
        disabled={loading}
        style={{
          padding: "10px 16px",
          background: "#2e7d32",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        {loading ? "Résumé en cours..." : "Résumé"}
      </button>

      {summary && (
        <div style={{ marginTop: "20px" }}>
          <h3>Résumé :</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}
