import React, { useState } from "react";
import "./LoginPage.css";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import TwoFAPage from "./TwoFAPage";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState("login");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");

    const result = await login(username, password);

    if (result?.twoFactor) {
      setStep("2fa");
      return;
    }

    if (result?.error) {
      setError(result.error);
      return;
    }

    // ✅ normal login success
    navigate("/");
  }

  // ✅ 2FA step (no props, no crashes)
  if (step === "2fa") {
    return <TwoFAPage />;
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card animated">
        <h2>Welcome Back</h2>
        <p className="subtext">We're glad you're here 💚</p>

        <form onSubmit={submit} className="auth-form">
          <input
            placeholder="Username"
            className="auth-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            className="auth-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="auth-btn">Login</button>
        </form>

        {error && <div className="error-msg">{error}</div>}

        <div className="auth-links">
          <Link to="/password-reset">Forgot Password?</Link>
          {" · "}
          <Link to="/signup">Create Account</Link>
        </div>
      </div>
    </div>
  );
}
