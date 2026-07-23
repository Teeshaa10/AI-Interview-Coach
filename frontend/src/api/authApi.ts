import { apiClient } from "@/api/client";
import type { LoginPayload, RegisterPayload, TokenResponse, User } from "@/types/auth";

/**
 * Every path below is exactly as mounted in backend/app/main.py -
 * app.include_router(auth_router) with no /api/v1 prefix (see
 * app/api/v1/auth.py: APIRouter(prefix="/auth")).
 */
export const authApi = {
  register: async (payload: RegisterPayload): Promise<User> => {
    const { data } = await apiClient.post<User>("/auth/register", payload);
    return data;
  },

  login: async (payload: LoginPayload): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>("/auth/login", payload);
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await apiClient.get<User>("/auth/me");
    return data;
  },
};
