import React from "react";
import CompanySearch from "./CompanySearch";


export default function ChatHeader({ showHistory, setShowHistory, sendMessage }) {
  return (
    <div className="chatgpt-header">
      {/* Titre */}
      <div className="header-title">
      Navibot
      </div>

      {/* Barre de recherche */}
      <div className="header-search">
        <CompanySearch sendMessage={sendMessage} />
      </div>

      {/* Bouton pour afficher/cacher l'historique */}
      <div className="header-right">
        <button
          className="history-toggle"
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? "🡸" : "🡺"}
        </button>
      </div>
    </div>
  );
}
