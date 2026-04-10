import React from "react";
import "./ThemePicker.css";

const THEMES = [
  { key: "teal", label: "Teal Breeze", color: "#2f8f8b" },
  { key: "soft-blue", label: "Soft Blue", color: "#4a8fe7" },
  { key: "sage", label: "Sage Calm", color: "#8bbf92" },
];

export default function ThemePicker({ setTheme, parentLabelId }) {
  return (
    <div
      role="list"
      aria-labelledby={parentLabelId}
      className="theme-picker-container"
    >
      {THEMES.map((t) => (
        <button
          key={t.key}
          role="listitem"
          className="theme-dot-picker"
          style={{ backgroundColor: t.color }}
          onClick={() => {
            setTheme(t.key);
            localStorage.setItem("mentalchat_theme", t.key);
          }}
          aria-label={`Select theme ${t.label}`}
        >
          <span className="theme-tooltip">{t.label}</span>
        </button>
      ))}
    </div>
  );
}
