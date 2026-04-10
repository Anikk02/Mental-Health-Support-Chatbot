import React, { useEffect, useState } from "react";
import "./MoodPage.css";

import MoodTracker from "../components/MoodTracker";
import { useAuth } from "../hooks/useAuth";

export default function MoodPage() {
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
          <p className="login-quote">
            Please sign in to access your mood insights.
          </p>

          <div className="login-gate-buttons">
            <a href="/login" className="gate-btn primary">Login</a>
            <a href="/signup" className="gate-btn secondary">Create Account</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-page-card">
      <MoodTracker userId={user.username} />
    </div>
  );
}
