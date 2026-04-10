import React, { useEffect, useState } from "react";
import "./EmailVerifyPage.css";

import { useAuth } from "../hooks/useAuth";
import { useSearchParams } from "react-router-dom";

export default function EmailVerifyPage() {
  const { verifyEmail } = useAuth();
  const [params] = useSearchParams();
  const [message, setMessage] = useState("Verifying your email...");
  const [isSuccess, setIsSuccess] = useState(null);

  useEffect(() => {
    async function run() {
      const token = params.get("token");
      const uid = params.get("uid");

      const r = await verifyEmail(token, uid);

      if (r?.error) {
        setMessage("Invalid or expired verification link.");
        setIsSuccess(false);
      } else {
        setMessage("Your email has been successfully verified! 🎉");
        setIsSuccess(true);
      }
    }

    run();
  }, []);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Email Verification</h2>
        <p className="auth-sub">{message}</p>

        {isSuccess && (
          <a href="/login" className="auth-link">
            Continue to Login
          </a>
        )}

        {isSuccess === false && (
          <a href="/signup" className="auth-link">
            Go back to Signup
          </a>
        )}
      </div>
    </div>
  );
}
