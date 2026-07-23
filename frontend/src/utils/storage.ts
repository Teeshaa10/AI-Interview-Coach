/**
 * Single, consistent place for the access-token key so it can never drift
 * between the API client, AuthContext, and anywhere else that needs it.
 */
const TOKEN_KEY = "aic_access_token";
const USER_KEY = "aic_user";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getStoredUserRaw(): string | null {
  return localStorage.getItem(USER_KEY);
}

export function setStoredUserRaw(userJson: string): void {
  localStorage.setItem(USER_KEY, userJson);
}

export function clearAuthStorage(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
