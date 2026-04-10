import React, { useEffect, useState } from "react";
import { fetchHistory } from "../api/apiClient";
import { motion } from "framer-motion";
import { FiClock, FiMessageCircle, FiUser, FiCornerDownRight } from "react-icons/fi";
import "./HistoryList.css";

export default function HistoryList({ userId }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
  async function load() {
    try {
      const r = await fetchHistory(userId, 50);

      const raw = r?.data;

      // Normalize response
      const list = Array.isArray(raw)
        ? raw
        : Array.isArray(raw?.items)
        ? raw.items
        : [];

      setItems(list);
    } catch (e) {
      console.error("history fetch error", e);
      setItems([]);
    }
  }

  if (userId) load();
}, [userId]);


  if (!items.length) {
    return (
      <motion.div
        className="muted"
        initial={{ opacity: 0.4 }}
        animate={{ opacity: 1 }}
      >
        No history yet
      </motion.div>
    );
  }

  return (
    <div className="history-container" role="region" aria-label="Conversation history">
      <h3 className="history-title">Conversation History</h3>

      <div className="history-scroll" role="list">
        {items.map((it, idx) => {
          const time = new Date(it.created_at).toLocaleString();

          return (
            <motion.div
              key={it.id || idx}
              role="listitem"
              className="history-card"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.04 }}
              tabIndex={0}
            >
              {/* HEADER */}
              <div className="history-header">
                <FiClock className="h-icon" />
                <span className="h-time">{time}</span>
              </div>

              {/* USER MESSAGE */}
              <div className="history-section">
                <FiUser className="h-icon user" />
                <div className="history-bubble user-bubble">
                  {it.user_input}
                </div>
              </div>

              {/* BOT RESPONSE */}
              <div className="history-section">
                <FiMessageCircle className="h-icon bot" />
                <div className="history-bubble bot-bubble">
                  {it.model_response}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
