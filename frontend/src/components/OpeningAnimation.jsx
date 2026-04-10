import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./OpeningAnimation.css";

/**
 * onFinish(action: "login" | "signup" | "forgot")
 */
export default function OpeningAnimation({ onFinish }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") {
        onFinish?.("login");
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onFinish]);

  return (
    <AnimatePresence>
      <motion.div
        className="opening-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        role="dialog"
        aria-modal="true"
      >
        <motion.div
          className="opening-card"
          initial={{ scale: 0.96, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Illustration */}
          <div className="opening-illustration" aria-hidden>
            <svg width="120" height="120" viewBox="0 0 120 120">
              <defs>
                <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stopColor="#a7f0ea" />
                  <stop offset="1" stopColor="#4db0a3" />
                </linearGradient>
              </defs>
              <rect rx="20" width="120" height="120" fill="url(#g)" />
              <g transform="translate(18,30)" fill="#fff">
                <circle cx="18" cy="18" r="16" opacity="0.95" />
                <rect x="44" y="8" width="38" height="24" rx="6" opacity="0.95" />
              </g>
            </svg>
          </div>

          {/* Text */}
          <h2>LumoAI</h2>
          <p className="opening-subtext">
            A calm, private space for emotional support and reflection.
          </p>

          {/* Actions */}
          <div className="opening-actions">
            <button
              className="primary"
              onClick={() => onFinish?.("login")}
            >
              Login
            </button>

            <button
              className="secondary"
              onClick={() => onFinish?.("signup")}
            >
              Create Account
            </button>

            <button
              className="link"
              onClick={() => onFinish?.("forgot")}
            >
              Forgot Password?
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
