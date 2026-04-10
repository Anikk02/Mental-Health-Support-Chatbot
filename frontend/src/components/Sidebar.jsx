import React from "react";
import { FiHome, FiUser, FiLogOut, FiSettings, FiActivity, FiFeather, FiClock } from "react-icons/fi";
import { Link, useNavigate } from "react-router-dom";
import "./Sidebar.css";
import ThemePicker from "./ThemePicker";
import { useAuth } from "../hooks/useAuth";

export default function Sidebar({ setTheme }) {
  const { user, logout } = useAuth();
  const nav = useNavigate();

  return (
    <aside
      className="sidebar"
      aria-label="Main navigation"
    >
      {/* Header / Branding */}
      <div className="sidebar-header">
        {/*<div className="sidebar-logo">💚</div>*/}
        <div>
          <h2 className="sidebar-title">LAMIRA</h2>
          <p className="sidebar-sub">Gentle support • Healing space</p>
        </div>
      </div>

      {/* Theme Picker */}
      <div className="sidebar-block">
        <h4 id="theme-heading" className="sr-only">Theme Picker</h4>
        <ThemePicker setTheme={setTheme} parentLabelId="theme-heading" />
      </div>

      {/* Main Navigation */}
      <nav className="sidebar-nav" aria-label="Primary navigation">
        <Link to="/" className="sidebar-item">
          <FiHome /> Chat
        </Link>

        <Link to="/history" className="sidebar-item">
          <FiClock /> History
        </Link>


        <Link to="/mood" className="sidebar-item">
          <FiActivity /> Mood Tracker
        </Link>

        <Link to="/analysis" className="sidebar-item">
          <FiFeather /> Response Analysis
        </Link>

        <Link to="/settings" className="sidebar-item">
          <FiSettings /> Settings
        </Link>
      </nav>

      {/* Footer Section */}
      <div className="sidebar-footer">
        {user ? (
          <>
            <div className="sidebar-username">
              <FiUser /> {user.username}
            </div>

            <button
              className="sidebar-item logout"
              onClick={logout}
            >
              <FiLogOut /> Logout
            </button>
          </>
        ) : (
          <button
            className="sidebar-item"
            onClick={() => nav("/login")}
          >
            <FiUser /> Login / Signup
          </button>
        )}
      </div>
    </aside>
  );
}
