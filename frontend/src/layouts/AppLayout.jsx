import React, { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../pages/ChatPage.css";

export default function AppLayout() {
  const location = useLocation();
  const isDesktop = window.innerWidth >= 1025;

  // Desktop = open by default
  const [sidebarOpen, setSidebarOpen] = useState(isDesktop);

  /* --------------------------------
     AUTO CLOSE ON ROUTE CHANGE (MOBILE ONLY)
  -------------------------------- */
  useEffect(() => {
    if (!isDesktop) {
      setSidebarOpen(false);
    }
  }, [location.pathname, isDesktop]);

  /* --------------------------------
     BODY SCROLL LOCK (MOBILE ONLY)
  -------------------------------- */
  useEffect(() => {
    if (!isDesktop) {
      document.body.setAttribute(
        "data-sidebar-open",
        sidebarOpen ? "true" : "false"
      );
    } else {
      document.body.removeAttribute("data-sidebar-open");
    }
  }, [sidebarOpen, isDesktop]);

  return (
    <div
      className="app-layout"
      data-sidebar={
        isDesktop
          ? "open"                 // desktop: layout sidebar
          : sidebarOpen
          ? "open"                 // mobile open
          : "closed"               // mobile closed
      }
    >
      {/* HAMBURGER — ALL SCREENS */}
      <button
        className={`hamburger-btn ${sidebarOpen ? "open" : ""}`}
        onClick={() => setSidebarOpen(p => !p)}
        aria-label="Toggle sidebar"
      >
        <span />
        <span />
        <span />
      </button>

      {/* BACKDROP — MOBILE ONLY */}
      {!isDesktop && (
        <div
          className="sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
          aria-hidden
        />
      )}

      {/* SIDEBAR */}
      <aside className="sidebar-container">
        <Sidebar />
      </aside>

      {/* PAGE CONTENT */}
      <main className="chat-main-content">
        <Outlet />
      </main>
    </div>
  );
}
