import React, { useEffect, useState } from "react";
import "./ResponseAnalysis.css";

import { fetchResponseAnalysis } from "../api/apiClient";
import { motion } from "framer-motion";
import { FiBarChart2, FiMessageCircle, FiBookOpen, FiTrendingUp } from "react-icons/fi";

export default function ResponseAnalysis({ userId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const r = await fetchResponseAnalysis(userId);
        setData(r.data || {});
      } catch (e) {
        console.error("analysis fetch error", e);
      }
    }
    load();
  }, [userId]);

  if (!data)
    return (
      <motion.div
        className="muted"
        initial={{ opacity: 0.4 }}
        animate={{ opacity: 1 }}
      >
        Loading analysis...
      </motion.div>
    );

  const insightCards = [
    {
      label: "Total Records",
      value: data.count || 0,
      icon: <FiBookOpen />,
      color: "#2f8f8b",
    },
    {
      label: "Avg Word Overlap",
      value: data.avg_word_overlap?.toFixed(3) || 0,
      icon: <FiMessageCircle />,
      color: "#4a8fe7",
    },
    {
      label: "Avg Length Ratio",
      value: data.avg_length_ratio?.toFixed(3) || 0,
      icon: <FiTrendingUp />,
      color: "#8bbf92",
    },
    {
      label: "Short Responses",
      value: data.short_responses?.length || 0,
      icon: <FiBarChart2 />,
      color: "#c57fd0",
    },
  ];

  return (
    <motion.div
      className="analysis-container"
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3 className="analysis-title">Response Analysis</h3>

      <div className="analysis-grid">
        {insightCards.map((c, i) => (
          <motion.div
            key={i}
            className="analysis-card-enhanced"
            style={{ borderLeft: `6px solid ${c.color}` }}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
          >
            <div className="analysis-icon" style={{ color: c.color }}>
              {c.icon}
            </div>
            <div className="analysis-metric">
              <div className="metric-value">{c.value}</div>
              <div className="metric-label">{c.label}</div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
