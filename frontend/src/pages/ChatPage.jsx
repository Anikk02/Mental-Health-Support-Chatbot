import React, { useEffect, useState } from "react";
import ChatWindow from "../components/ChatWindow";
import CharacterTransition from "../components/CharacterTransition";
import OpeningAnimation from "../components/OpeningAnimation";
import { useAuth } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

export default function ChatPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const hasSeenIntro =
    sessionStorage.getItem("lumo_intro_seen") === "true";

  const [mode, setMode] = useState("loading");
  // loading | character | opening | redirect | chat

  useEffect(() => {
    if (user === undefined) {
      setMode("loading");
      return;
    }

    if (!hasSeenIntro) {
      setMode("character");
      return;
    }

    if (!user) {
      setMode("redirect");
      return;
    }

    setMode("chat");
  }, [user, hasSeenIntro]);

  /* ---------------- REDIRECT ---------------- */
  useEffect(() => {
    if (mode === "redirect") {
      navigate("/login", { replace: true });
    }
  }, [mode, navigate]);

  /* ---------------- RENDER ---------------- */

  if (mode === "loading") return null;

  if (mode === "character") {
    return (
      <CharacterTransition
        onFinish={() => {
          sessionStorage.setItem("lumo_intro_seen", "true");
          setMode("opening");
        }}
      />
    );
  }

  if (mode === "opening") {
    return (
      <OpeningAnimation
        onFinish={(action) => {
          if (action === "login") navigate("/login");
          if (action === "signup") navigate("/signup");
          if (action === "forgot") navigate("/password-reset");
        }}
      />
    );
  }

  if (mode !== "chat") return null;

  return <ChatWindow userId={user.username} />;
}
