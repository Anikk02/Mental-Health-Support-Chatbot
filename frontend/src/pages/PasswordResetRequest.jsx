import React, { useState } from "react";
import "./PasswordResetRequest.css";
import { requestPasswordReset } from "../api/apiClient";

export default function PasswordResetRequest() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setMsg("");
    setErr("");

    try {
      await requestPasswordReset(email);
      setMsg("If an account exists, a password-reset link has been sent.");
    } catch {
      setErr("Something went wrong. Please try again.");
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Reset Password</h2>
        <p className="auth-sub">
          Enter your email and we’ll send you a secure reset link ✉️
        </p>

        <form onSubmit={submit}>
          <input
            className="auth-input"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            required
          />

          <button className="auth-btn">Send Reset Link</button>
        </form>

        {err && <p style={{ color: "red", marginTop: 10 }}>{err}</p>}
        {msg && <p style={{ color: "green", marginTop: 10 }}>{msg}</p>}

        <a href="/login" className="auth-link">
          Back to Login
        </a>
      </div>
    </div>
  );
}
