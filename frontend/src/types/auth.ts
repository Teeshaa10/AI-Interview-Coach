/**
 * Mirrors backend/app/schemas/user.py exactly.
 */

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}
