import React, { useState } from "react";
import "./TwoFAPage.css";
import { useAuth } from "../hooks/useAuth";
import { useNavigate, Link } from "react-router-dom";

export default function TwoFAPage() {
  const { verify2FA } = useAuth();
  const navigate = useNavigate();

  const [otp, setOtp] = useState("");
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    setMsg("");

    const r = await verify2FA({
      otp_code: otp,
      otp_code_secret: null,
    });

    if (r?.error) {
      setErr("Invalid OTP. Please try again.");
      return;
    }

    setMsg("OTP verified! Logging you in...");

    // ✅ SPA-safe redirect
    setTimeout(() => {
      navigate("/", { replace: true });
    }, 800);
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Two-Factor Authentication</h2>
        <p className="auth-sub">
          Enter the 6-digit OTP from your authenticator app 🔐
        </p>

        <form onSubmit={submit}>
          <input
            className="auth-input"
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            maxLength={6}
            inputMode="numeric"
            pattern="[0-9]{6}"
            required
          />

          <button className="auth-btn">Verify</button>
        </form>

        {err && <p style={{ color: "red", marginTop: 10 }}>{err}</p>}
        {msg && <p style={{ color: "green", marginTop: 10 }}>{msg}</p>}

        {/* ✅ SPA-safe link */}
        <Link to="/login" className="auth-link">
          Back to Login
        </Link>
      </div>
    </div>
  );
}
