import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { authApi } from "@/api/authApi";
import { registerUnauthorizedHandler } from "@/api/client";
import type { LoginPayload, RegisterPayload, User } from "@/types/auth";
import {
  clearAuthStorage,
  getStoredToken,
  getStoredUserRaw,
  setStoredToken,
  setStoredUserRaw,
} from "@/utils/storage";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isCheckingAuth: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  const logout = useCallback(() => {
    clearAuthStorage();
    setUser(null);
  }, []);

  // A 401 from anywhere in the app funnels through here so auth state and
  // the UI stay in sync without every call site needing to know about it.
  useEffect(() => {
    registerUnauthorizedHandler(logout);
  }, [logout]);

  // On first load, trust a cached user for an instant UI, then verify it
  // against GET /auth/me. If the token is gone or invalid, log out.
  useEffect(() => {
    const token = getStoredToken();
    const cachedUser = getStoredUserRaw();

    if (!token) {
      setIsCheckingAuth(false);
      return;
    }

    if (cachedUser) {
      try {
        setUser(JSON.parse(cachedUser) as User);
      } catch {
        // Ignore a corrupted cache entry; /auth/me below is authoritative.
      }
    }

    authApi
      .me()
      .then((freshUser) => {
        setUser(freshUser);
        setStoredUserRaw(JSON.stringify(freshUser));
      })
      .catch(() => {
        clearAuthStorage();
        setUser(null);
      })
      .finally(() => setIsCheckingAuth(false));
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const response = await authApi.login(payload);
    setStoredToken(response.access_token);
    setStoredUserRaw(JSON.stringify(response.user));
    setUser(response.user);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    await authApi.register(payload);
    // Registration does not return a token (see UserResponse in
    // schemas/user.py) - log in right after so the flow feels seamless.
    await login({ email: payload.email, password: payload.password });
  }, [login]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isCheckingAuth,
      login,
      register,
      logout,
    }),
    [user, isCheckingAuth, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
