import React, { useEffect, useRef, useState } from "react";
import "./ChatWindow.css";

import { motion, AnimatePresence } from "framer-motion";
import { postChat, fetchHistory } from "../api/apiClient";
import { toDatasetPayload } from "../utils/datasetFormatter";
import { useAuth } from "../hooks/useAuth";

export default function ChatWindow({ userId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const composerRef = useRef(null);
  const endRef = useRef(null);
  const liveRef = useRef(null);
  const { user } = useAuth();

  // ------------------ Formatting helpers ------------------
  // Format bot text:
  //  - insert line breaks before "1.", "2.", etc.
  //  - wrap subpoint titles (text before colon after a number) with a span
  //  - return HTML string (we render with dangerouslySetInnerHTML for bot)
  function formatMessage(text) {
    if (!text) return "";

    let s = String(text).trim();

    // insert newline before every numbered bullet "1.", "2." etc.
    s = s.replace(/(\d+\.)/g, "\n$1");

    // wrap the subpoint title (text after number until the next colon) in a span
    // Example: "1. Challenge negative thoughts: do X" -> '1. <span class="subpoint-title">Challenge negative thoughts:</span> do X'
    s = s.replace(/(\d+\.)\s*([^:]+:)/g, '$1 <span class="subpoint-title">$2</span>');

    // Now split lines and wrap them in <div>
    const lines = s.split("\n").map((line) => {
      const clean = line.trim();
      if (!clean) return "";
      // We intentionally DO NOT escape here so span remains HTML.
      // If you later need to allow arbitrary user HTML, you must sanitize it.
      return `<div>${clean}</div>`;
    });

    return lines.join("");
  }

  // ------------------ LOAD HISTORY ------------------
  useEffect(() => {
  const resolvedUser = userId ?? user?.username;
  if (!resolvedUser) return;

  async function load() {
    try {
      const res = await fetchHistory(resolvedUser, 50);
      let docs = [];

      if (Array.isArray(res?.data)) docs = res.data;
      else if (Array.isArray(res?.data?.items)) docs = res.data.items;
      else if (Array.isArray(res?.data?.docs)) docs = res.data.docs;
      else if (res?.data && typeof res.data === "object") {
        docs = Object.values(res.data);
      }

      const formatted = [];
      [...docs].reverse().forEach((d) => {
        formatted.push({ from: "user", text: d.user_input });
        formatted.push({ from: "bot", text: d.model_response });
      });

      setMessages(formatted);
    } catch (e) {
      console.error("History error", e);
      setMessages([]);
    }
  }

  load();
}, [userId, user]);




  // ------------------ AUTO SCROLL ------------------
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ------------------ SEND MESSAGE ------------------
  async function sendMessage() {
    if (!input.trim()) return;

    const text = input.trim();

    setMessages((prev) => [...prev, { from: "user", text, time: new Date() }]);
    setInput("");
    setIsTyping(true);
    setLoading(true);

    const payload = toDatasetPayload({ userId: userId || user?.username, text });

    try {
      const res = await postChat(payload);
      const rawBotMsg = res.data.bot_response || "I'm here to help.";

      // format the response HTML BEFORE storing
      const botMsg = formatMessage(rawBotMsg); // <-- important

      await new Promise((r) => setTimeout(r, 400 + Math.random() * 400));

      setMessages((prev) => [
        ...prev,
        {
          from: "bot",
          text: botMsg,     // formatted HTML
          crisis: res.data.crisis,
          time: new Date(),
        },
      ]);

      if (liveRef.current) liveRef.current.textContent = `New reply: ${rawBotMsg}`;
    } catch (err) {
      console.error("send error", err);
    } finally {
      setIsTyping(false);
      setLoading(false);
      composerRef.current?.focus();
    }
  }

  // ------------------ ENTER KEY SEND ------------------
  function onEnter(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="chat-window-enhanced">

      {/* HEADER */}
      <header className="chat-header-enhanced">
        <div className="chat-header-row">
          <div className="chat-title">LAMIRA</div>
        </div>

        <div className="chat-subtitle">
          You're not alone. I'm here for you 💚
        </div>
      </header>


      {/* MESSAGES */}
      <section aria-live="polite" className="chat-body-enhanced">
        <AnimatePresence>
          {messages.map((m, i) => (
            <motion.div
              key={i + "-" + (m.text || "").slice(0, 10)}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.22 }}
              className={`bubble-row ${m.from}`}
            >
              {/* AVATAR — ONLY FOR BOT */}
              <div className="avatar">
                {m.from === "bot" ? "🧠" : ""}
              </div>

              {/* MESSAGE BUBBLE */}
              <div className={`bubble ${m.from}`}>
                {m.from === "bot" ? (
                  // Bot messages are pre-formatted HTML
                  <div
                    className="bubble-text"
                    dangerouslySetInnerHTML={{ __html: m.text }}
                  />
                ) : (
                  <div className="bubble-text">{m.text}</div>
                )}
              </div>

              {/* CRISIS INDICATOR BELOW BUBBLE */}
              {m.from === "bot" && m.crisis && (
                <div className="crisis-badge-inline">
                  ⚠ Crisis detected — Please reach out for help.
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* TYPING INDICATOR */}
        {isTyping && (
          <div className="bubble-row bot">
            <div className="avatar">🧠</div>
            <div className="bubble typing-bubble">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          </div>
        )}

        <div ref={endRef}></div>
      </section>

      {/* SCREEN READER LIVE REGION */}
      <div aria-live="polite" ref={liveRef} className="sr-only"></div>

      {/* FOOTER INPUT */}
      <footer className="chat-footer-enhanced">
        <textarea
          ref={composerRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onEnter}
          placeholder="Type a message..."
          className="composer"
        />

        <button
          onClick={sendMessage}
          className="send-btn-enhanced"
          disabled={loading}
        >
          {loading ? "..." : "Send"}
        </button>
      </footer>
    </div>
  );
}
