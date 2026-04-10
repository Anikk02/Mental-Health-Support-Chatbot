import React, { useEffect, useState } from "react";
import { fetchMood } from "../api/apiClient";
import { motion } from "framer-motion";
import "./MoodTracker.css";

import {
  FiHeart,
  FiAlertTriangle,
  FiSmile,
  FiBarChart2,
  FiTarget,
  FiZap,
  FiShield
} from "react-icons/fi";

export default function MoodTracker({ userId }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const r = await fetchMood(userId);
        setStats(r.data || {});
      } catch (e) {
        console.error("mood error", e);
      }
    }
    load();
  }, [userId]);

  if (!stats) return <div className="muted">Loading mood stats…</div>;

  const emotions = stats.emotion_counts || {};
  const triggers = stats.trigger_counts || {};
  const escalations = stats.escalation_counts || {};

  const dominantEmotion =
    Object.entries(emotions).sort((a, b) => b[1] - a[1])[0]?.[0] || "neutral";

  const stabilityScore = Math.max(
    0,
    100 - Math.round((stats.avg_risk_intensity ?? 0) * 100)
  );

  function getRiskLevel(avg, count) {
    if (avg > 0.7 || count > 3) return "CRITICAL";
    if (avg > 0.4) return "HIGH";
    if (avg > 0.2) return "MEDIUM";
    return "LOW";
  }

  const riskLevel = getRiskLevel(
    stats.avg_risk_intensity ?? 0,
    stats.risk_count ?? 0
  );

  return (
    <motion.div
      className="mood-container"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3 className="mood-title">Mood Tracker</h3>

      {/* ===== Mental State Overview ===== */}
      <div className="mood-overview">
        <div className={`risk-badge risk-${riskLevel.toLowerCase()}`}>
          <FiShield /> Current Risk Level: {riskLevel}
        </div>

        <div className="overview-row">
          <span>Dominant Emotion:</span>
          <b>{dominantEmotion}</b>
        </div>

        <div className="overview-row">
          <span>Emotional Stability:</span>
          <b>{stabilityScore}/100</b>
        </div>
      </div>

      {/* ===== Main Stats Grid ===== */}
      <div className="mood-grid">
        <div className="mood-card">
          <FiBarChart2 className="mood-icon" />
          <div className="mood-value">{stats.count}</div>
          <div className="mood-label">Messages Analyzed</div>
        </div>

        <div className="mood-card">
          <FiSmile className="mood-icon" />
          <div className="mood-meter">
            <div
              className="meter-fill"
              style={{
                width: `${(stats.avg_sentiment + 1) * 50}%`,
              }}
            />
          </div>
          <div className="mood-label">
            Avg Sentiment: {(stats.avg_sentiment ?? 0).toFixed(3)}
          </div>
        </div>

        <div className="mood-card">
          <FiHeart className="mood-icon" />
          <div className="mood-meter">
            <div
              className="meter-fill"
              style={{ width: `${(stats.avg_empathy ?? 0) * 100}%` }}
            />
          </div>
          <div className="mood-label">
            Avg Empathy: {(stats.avg_empathy ?? 0).toFixed(3)}
          </div>
        </div>

        <div className="mood-card">
          <FiAlertTriangle className="mood-icon risk" />
          <div className="mood-value">{stats.risk_count}</div>
          <div className="mood-label">Risk Indicators</div>
        </div>

        <div className="mood-card">
          <FiZap className="mood-icon" />
          <div className="mood-value">
            {(stats.avg_risk_intensity ?? 0).toFixed(3)}
          </div>
          <div className="mood-label">Avg Risk Intensity</div>
        </div>

        <div className="mood-card">
          <FiTarget className="mood-icon" />
          <div className="mood-value">{stats.avg_input_length}</div>
          <div className="mood-label">Avg Input Length</div>
        </div>
      </div>

      {/* ===== CTA ===== */}
      <motion.div className="risk-cta">
        <div>
          <h4>Risk Assessment</h4>
          <p>
            Understand how risk levels and escalation actions are determined.
          </p>
          <a href="/risk-assessment">View Risk Assessment →</a>
        </div>
      </motion.div>
    </motion.div>
  );
}
