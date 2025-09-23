import React, { useState } from "react";

export default function CompanySearch({ sendMessage }) {
  const [query, setQuery] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      const response = await fetch("http://localhost:8000/company-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query }),
      });

      const data = await response.json();

      
      sendMessage({ text: data.response, sender: "company" });
    } catch (err) {
      console.error(err);
      sendMessage({ text: "Erreur lors de la recherche", sender: "company" });
    }

    setQuery("");
  };

  return (
    <div className="company-search">
  <label className="company-search-label">
    Que voulez-vous connaître sur Navitrends ?
  </label>
  <input
    type="text"
    placeholder="Posez votre question..."
    value={query}
    onChange={(e) => setQuery(e.target.value)}
    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
    className="company-search-input"
  />
  <button onClick={handleSearch} className="company-search-btn">
    🔍
  </button>
</div>

  );
}
