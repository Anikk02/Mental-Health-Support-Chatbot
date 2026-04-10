import React, { useEffect, useState } from "react";
import "./AccountSettings.css";

import * as QRCode from "qrcode";
import { useAuth } from "../hooks/useAuth";
import {
  request2FASetup,
  confirm2FAVerify,
  disable2FA,
  resendVerification,
} from "../api/apiClient";

export default function AccountSettings() {
  const { user, logout } = useAuth();

  const [qr, setQR] = useState(null);
  const [secret, setSecret] = useState(null);
  const [otp, setOtp] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [avatar, setAvatar] = useState(null);

  useEffect(() => {
    if (user?.two_fa_enabled) setTwoFAEnabled(true);
  }, [user]);

  function handleAvatar(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setAvatar(reader.result);
    reader.readAsDataURL(file);
  }

  async function enable2FA() {
    setErr(""); 
    setMsg("");
    const r = await request2FASetup(user.username);
    setQR(r.data.otp_auth_url);
    setSecret(r.data.secret);
  }

  async function verify2FA() {
    setErr("");
    setMsg("");

    try {
      await confirm2FAVerify({
        username: user.username,
        otp_code: otp,
        otp_code_secret: secret,
      });

      setMsg("2FA Enabled Successfully!");
      setTwoFAEnabled(true);
      setQR(null);
      setSecret(null);
      setOtp("");
    } catch {
      setErr("Invalid OTP");
    }
  }

  async function disable2FAHandler() {
    await disable2FA(user.username);
    setTwoFAEnabled(false);
    setMsg("2FA Disabled");
  }

  async function resendVerifyEmail() {
    try {
      await resendVerification(user.email);
      setMsg("Verification email sent!");
    } catch {
      setErr("Failed to send email");
    }
  }

  return (
    <div className="settings-wrapper">
      <div className="settings-card-rect">

        <h2 className="settings-title">Account Settings</h2>
        <p className="settings-sub">Manage your profile & security</p>

        <div className="settings-grid">

          {/* LEFT COLUMN — PROFILE */}
          <div className="settings-left">

            <h3 className="section-title center">Profile</h3>

            <div className="profile-row column-center">
              <div className="profile-pic-wrap">
                <img
                  src={avatar || "/default-avatar.png"}
                  alt="profile"
                  className="profile-pic"
                />

                <label>
                  <input
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={handleAvatar}
                  />
                  <span className="upload-btn">Upload</span>
                </label>
              </div>

              <div className="profile-info center">
                <p className="profile-name"><b>Username:</b> {user?.username}</p>
              </div>
            </div>

            {!user?.is_email_verified ? (
              <button className="btn-outline full-btn" onClick={resendVerifyEmail}>
                Resend Verification Email
              </button>
            ) : (
              <div className="success-text small">Email Verified</div>
            )}

            <button className="logout-btn full-btn" onClick={logout}>
              Logout
            </button>

          </div>

          {/* RIGHT COLUMN — 2FA */}
          <div className="settings-right">

            <h3 className="section-title center">Two-Factor Authentication (2FA)</h3>

            <div className="switch-row">
              <span>Enable 2FA</span>

              <label className="switch">
                <input
                  type="checkbox"
                  checked={twoFAEnabled}
                  onChange={() =>
                    twoFAEnabled ? disable2FAHandler() : enable2FA()
                  }
                />
                <span className="slider"></span>
              </label>
            </div>

            {/* Placeholder before enabling 2FA */}
            {!qr && !twoFAEnabled && (
              <div className="placeholder-box">
                <p>Click the switch to enable 2FA & generate QR code.</p>
              </div>
            )}

            {/* QR + OTP UI */}
            {qr && (
              <div className="qr-box">
                <p>Scan this QR with Google Authenticator:</p>

                <canvas
                  ref={(el) => el && QRCode.toCanvas(el, qr, { width: 150 })}
                />

                <p className="secret-label">Secret: {secret}</p>

                <input
                  className="input"
                  placeholder="Enter 6-digit OTP"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  maxLength={6}
                />

                <button className="btn-primary full-btn" onClick={verify2FA}>
                  Verify OTP
                </button>
              </div>
            )}

            {/* After 2FA verified */}
            {twoFAEnabled && !qr && (
              <div className="success-text center">
                2FA is enabled on your account.
              </div>
            )}

          </div>
        </div>

        {msg && <p className="success-text center">{msg}</p>}
        {err && <p className="error-text center">{err}</p>}
      </div>
    </div>
  );
}
