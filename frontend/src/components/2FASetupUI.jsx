import React from "react";
import QRCode from "qrcode.react";
import "./2FASetupUI.css";


export default function TwoFASetupUI({ otpUrl, secret, onVerify, otp, setOtp }) {
  return (
    <div className="twofa-setup">
      <h4>Scan QR code</h4>
      <QRCode value={otpUrl} size={160} />
      <p>Or enter secret: <strong>{secret}</strong></p>

      <input placeholder="Enter OTP" value={otp} onChange={(e) => setOtp(e.target.value)} />
      <button onClick={onVerify}>Verify</button>
    </div>
  );
}
