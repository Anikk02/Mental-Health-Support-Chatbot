import React, { useState } from "react";
import "./PasswordResetConfirm.css";
import { confirmPasswordReset } from "../api/apiClient";
import { useSearchParams } from "react-router-dom";


export default function PasswordResetConfirm() {
  const [params] = useSearchParams();
  const token = params.get("token");

  console.log("RESET TOKEN:", token);

  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

async function submit(e) {
  e.preventDefault();
  setErr("");
  setMsg("");

  if (!token) {
    setErr("Invalid or expired reset link. Please request a new one.");
    return;
  }

  // ✅ Frontend validation
  if (password.length < 6) {
    setErr("Password must be at least 6 characters long.");
    return;
  }

  try {
    const r = await confirmPasswordReset(token, password);

    if (r?.data?.ok) {
      setMsg("Password updated successfully! You can now login.");
      setPassword("");
    } else {
      setErr("Invalid or expired token. Try requesting a new link.");
    }
  } catch (e) {
    const detail = e?.response?.data?.detail;

    // ✅ Handle FastAPI 422 validation errors
    if (Array.isArray(detail)) {
      setErr(detail[0]?.msg || "Invalid input.");
    } else {
      setErr(detail || "Password reset failed. Please try again.");
    }
  }}

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Set New Password</h2>
        <p className="auth-sub">Choose a strong new password 🔒</p>

        <form onSubmit={submit}>
          <input
            className="auth-input"
            placeholder="New Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="auth-btn">Update Password</button>
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
