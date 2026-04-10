import React, { useEffect, useState } from "react";
import "./characterTransition.css";

export default function CharacterTransition({ onFinish }) {
  const [stage, setStage] = useState(0);

  const messages = [
    "It's okay to feel down sometimes...",
    "Take a slow, deep breath...",
    "You're becoming lighter, calmer...",
    "You're safe. Ready to begin your journey 💚"
  ];

  useEffect(() => {
    const timeouts = [];

    const timings = [0, 1600, 3200, 4800];

    timings.forEach((t, i) => {
      timeouts.push(
        setTimeout(() => setStage(i), t)
      );
    });

    timeouts.push(
      setTimeout(() => {
        onFinish?.();
      }, 6400)
    );

    // ✅ CLEANUP
    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, [onFinish]);

  return (
    <div className="character-trans-container enhanced-bg">
      <div className="particle p1"></div>
      <div className="particle p2"></div>
      <div className="particle p3"></div>

      <div className="character-wrapper enhanced-glow">
        <div className={`face stage-${stage}`}>
          <div className="eyebrows">
            <div className="brow left"></div>
            <div className="brow right"></div>
          </div>

          <div className="eyes">
            <div className="eye"></div>
            <div className="eye"></div>
          </div>

          <div className="mouth"></div>
        </div>
      </div>

      <p className="transition-text fade-text">
        {messages[stage]}
      </p>
    </div>
  );
}
