import React, { createContext, useContext, useEffect, useState } from "react";
import {
  login,
  signup,
  verifyEmail,
  confirm2FAVerify,
} from "../api/apiClient";

const AuthContext = createContext();

const ACCESS_KEY = "mentalchat_token";
const REFRESH_KEY = "mentalchat_refresh";
const USER_KEY = "mc_user";

export function AuthProvider({ children }) {
  // undefined = loading, null = logged out
  const [user, setUser] = useState(undefined);
  const [pending2FAUser, setPending2FAUser] = useState(null);

  // 🔹 HYDRATE FROM SESSION STORAGE ONLY
  useEffect(() => {
    const stored = sessionStorage.getItem(USER_KEY);
    setUser(stored ? JSON.parse(stored) : null);
  }, []);

  function storeUser(u) {
    if (!u) {
      sessionStorage.removeItem(USER_KEY);
    } else {
      sessionStorage.setItem(USER_KEY, JSON.stringify(u));
    }
    setUser(u);
  }

  async function handleLogin(username, password) {
    try {
      const res = await login(username, password);
      const { access_token, refresh_token } = res.data;

      sessionStorage.setItem(ACCESS_KEY, access_token);
      sessionStorage.setItem(REFRESH_KEY, refresh_token);

      storeUser({ username });
      return { ok: true };
    } catch (err) {
      if (err.twoFactorRequired) {
        setPending2FAUser(username);
        return { twoFactor: true };
      }
      return { error: err.response?.data?.detail || "Login failed" };
    }
  }

  async function handleSignup(data) {
    try {
      const r = await signup(data);
      return { ok: true, data: r.data };
    } catch (err) {
      return { error: "Signup failed" };
    }
  }

  async function verify2FA(payload) {
    try {
      await confirm2FAVerify({
        username: pending2FAUser,
        ...payload,
      });
      setPending2FAUser(null);
      return { ok: true };
    } catch {
      return { error: "Invalid OTP" };
    }
  }

  async function handleVerifyEmail(token, uid) {
    try {
      return (await verifyEmail(token, uid)).data;
    } catch {
      return { error: "Invalid or expired link" };
    }
  }

  function logout() {
    sessionStorage.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        login: handleLogin,
        signup: handleSignup,
        logout,
        verify2FA,
        verifyEmail: handleVerifyEmail,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
