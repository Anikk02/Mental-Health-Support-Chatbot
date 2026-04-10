import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";

/* =======================
   PAGES
   ======================= */

import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import EmailVerifyPage from "./pages/EmailVerifyPage";
import PasswordResetRequest from "./pages/PasswordResetRequest";
import PasswordResetConfirm from "./pages/PasswordResetConfirm";
import AccountSettings from "./pages/AccountSettings";

import MoodPage from "./pages/MoodPage";
import ResponseAnalysisPage from "./pages/ResponseAnalysisPage";
import HistoryPage from "./pages/HistoryPage";

/* =======================
   LAYOUT
   ======================= */

import AppLayout from "./layouts/AppLayout";

/* =======================
   ROUTER INNER
   ======================= */

function AppRouterInner() {
  const navigate = useNavigate();

  return (
    <Routes>
      {/* =========================
          APP LAYOUT (SIDEBAR + HAMBURGER)
          ========================= */}
      <Route element={<AppLayout />}>
        {/* MAIN CHAT */}
        <Route path="/" element={<ChatPage />} />

        {/* APP PAGES */}
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/mood" element={<MoodPage />} />
        <Route path="/analysis" element={<ResponseAnalysisPage />} />
        <Route path="/settings" element={<AccountSettings />} />
      </Route>

      {/* =========================
          AUTH PAGES (NO SIDEBAR)
          ========================= */}
      <Route
        path="/login"
        element={<LoginPage onSuccess={() => navigate("/")} />}
      />
      <Route
        path="/signup"
        element={<SignupPage onSuccess={() => navigate("/login")} />}
      />

      {/* =========================
          EMAIL / PASSWORD
          ========================= */}
      <Route path="/verify-email" element={<EmailVerifyPage />} />
      <Route path="/password-reset" element={<PasswordResetRequest />} />
      <Route
        path="/password-reset/confirm"
        element={<PasswordResetConfirm />}
      />
    </Routes>
  );
}

/* =======================
   ROUTER WRAPPER
   ======================= */

export default function AppRouter() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <AppRouterInner />
    </BrowserRouter>
  );
}
