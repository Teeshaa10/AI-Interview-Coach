import axios, { AxiosError } from "axios";

import { getStoredToken, clearAuthStorage } from "@/utils/storage";

const baseURL = import.meta.env.VITE_API_BASE_URL;

if (!baseURL) {
  // Fails loudly at startup rather than silently hitting a relative path.
  // eslint-disable-next-line no-console
  console.error(
    "VITE_API_BASE_URL is not set. Copy frontend/.env.example to frontend/.env and restart the dev server.",
  );
}

export const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Callback the AuthContext registers so a 401 anywhere in the app can
 * clear auth state and redirect to /login, without this module needing to
 * import React Router directly.
 */
let onUnauthorized: (() => void) | null = null;

export function registerUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      clearAuthStorage();
      onUnauthorized?.();
    }
    return Promise.reject(error);
  },
);

/**
 * The backend returns errors as {"detail": "<message>"} for domain errors,
 * or {"detail": [{"msg": "...", ...}, ...]} for Pydantic 422 validation
 * errors (see app/exceptions/handlers.py and FastAPI's default validation
 * error shape). This normalizes both into a single readable string.
 */
export function getApiErrorMessage(error: unknown, fallback = "Something went wrong. Please try again."): string {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => (typeof item === "object" && item !== null && "msg" in item ? String((item as { msg: unknown }).msg) : null))
        .filter((msg): msg is string => Boolean(msg));
      if (messages.length > 0) {
        return messages.join(" ");
      }
    }

    if (error.code === "ERR_NETWORK") {
      return "Could not reach the server. Is the backend running?";
    }
  }

  return fallback;
}
