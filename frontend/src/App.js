import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Chatbot from "./components/Chatbot/Chatbot";
import ResumePage from "./components/Chatbot/ResumePage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Chatbot />} />
        <Route path="/resume" element={<ResumePage />} />
      </Routes>
    </Router>
  );
}

export default App;
