import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

// -----------------------
// Token helpers
// -----------------------
const ACCESS_KEY = "mentalchat_token";
const REFRESH_KEY = "mentalchat_refresh";
const USER_KEY = "mc_user";

function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY);
}

function setTokens(access, refresh) {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

// -----------------------
// Refresh queue handling
// -----------------------
let isRefreshing = false;
let refreshSubscribers = [];

function onAccessTokenFetched(newToken) {
  refreshSubscribers.forEach((cb) => cb(newToken));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback) {
  refreshSubscribers.push(callback);
}

const api = axios.create({
  baseURL: API_BASE,
  timeout: 20000,
});

// Attach access token
api.interceptors.request.use((config) => {
  const t = getAccessToken();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// -----------------------
// Response Interceptor
// -----------------------
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const originalReq = err.config;

    // 2FA required
    if (
      err.response?.status === 403 &&
      err.response?.data?.detail === "two_factor_required"
    ) {
      return Promise.reject({ twoFactorRequired: true });
    }

    // Expired access token → attempt refresh
    if (err.response?.status === 401 && !originalReq._retry) {
      originalReq._retry = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        return Promise.reject(err);
      }

      // If a refresh is already happening → wait
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const r = await axios.post(`${API_BASE}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = r.data;

          setTokens(access_token, refresh_token);
          isRefreshing = false;
          onAccessTokenFetched(access_token);
        } catch (refreshErr) {
          isRefreshing = false;
          return Promise.reject(refreshErr);
        }
      }

      // Queue the retry until refresh finishes
      return new Promise((resolve) => {
        addRefreshSubscriber((newToken) => {
          originalReq.headers.Authorization = `Bearer ${newToken}`;
          resolve(api(originalReq));
        });
      });
    }

    return Promise.reject(err);
  }
);

// -----------------------
// AUTH API
// -----------------------
export const signup = (payload) =>
  api.post("/api/auth/signup", payload);

export const login = (username, password) => {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);
  return api.post("/api/auth/login", params);
};

export const verifyEmail = (token, uid) =>
  api.get(`/api/auth/verify-email?token=${token}&uid=${uid}`);

export const resendVerification = (email) =>
  api.post(`/api/auth/resend-verification?email=${email}`);


export const requestPasswordReset = (email) =>
  api.post("/api/auth/password-reset/request", { email });

export const confirmPasswordReset = (token, new_password) =>
  api.post("/api/auth/password-reset/confirm", { token, new_password });

// 2FA
export const request2FASetup = (username) =>
  api.post(`/api/auth/2fa/setup?username=${username}`);

export function confirm2FAVerify({ username, otp_code, otp_code_secret }) {
  return api.post("/api/auth/2fa/verify", {
    username,
    otp_code,
    otp_code_secret,
  });
}



export const disable2FA = (username) =>
  api.post(`/api/auth/2fa/disable?username=${username}`, { enable: false });

// -----------------------
// Chat API
// -----------------------
export const postChat = (payload) => api.post("/api/chat", payload);

// -----------------------
// History / Analysis
// -----------------------
export const fetchHistory = (uid, limit = 50) =>
  api.get(`/api/history?user_id=${uid}&limit=${limit}`);

export const fetchMood = (uid) =>
  api.get(`/api/mood?user_id=${uid}`);

export const fetchResponseAnalysis = (uid) =>
  api.get(`/api/response-analysis?user_id=${uid}`);

export default api;
