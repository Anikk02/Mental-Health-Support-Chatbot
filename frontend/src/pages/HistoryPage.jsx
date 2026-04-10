import React, { useEffect, useState } from "react";
import "./HistoryPage.css";

import HistoryList from "../components/HistoryList";
import { useAuth } from "../hooks/useAuth";

export default function HistoryPage() {
  const { user } = useAuth();

  const [theme, setTheme] = useState(
    localStorage.getItem("mentalchat_theme") || "teal"
  );

  useEffect(() => {
    document.body.setAttribute("data-theme", theme);
  }, [theme]);

  if (!user) {
    return (
      <div className="login-gate-container">
        <div className="login-gate-card">
          <h2>Login Required</h2>
          <p>Please sign in to view your chat history.</p>

          <div className="login-gate-buttons">
            <a className="gate-btn primary" href="/login">Login</a>
            <a className="gate-btn secondary" href="/signup">Create Account</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-card" style={{ padding: "20px" }}>
      <HistoryList userId={user.username} />
    </div>
  );
}
