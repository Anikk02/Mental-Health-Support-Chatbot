import React, { useState } from "react";
import "./SignupPage.css";
import { useAuth } from "../hooks/useAuth";

export default function SignupPage({ onSuccess }) {
  const { signup } = useAuth();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setMsg(null);
    setErr(null);

    const r = await signup({ username, email, password });

    if (r.error) {
      setErr(r.error);
      return;
    }

    setMsg("✨ Account created! Check your email to verify your account.");
    if (onSuccess && typeof onSuccess==="function") onSuccess();
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card animated">
        <h2>Create Your Account</h2>
        <p className="subtext">Begin your calm & supportive journey 💚</p>

        <form onSubmit={submit} className="auth-form">
          <input
            placeholder="Username"
            className="auth-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input
            placeholder="Email Address"
            className="auth-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            placeholder="Password"
            type="password"
            className="auth-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="auth-btn">Create Account</button>
        </form>

        {err && <div className="error-msg">{err}</div>}
        {msg && <div className="success-msg">{msg}</div>}

        <div className="auth-links">
          Already have an account? <a href="/login">Login</a>
        </div>
      </div>
    </div>
  );
}
