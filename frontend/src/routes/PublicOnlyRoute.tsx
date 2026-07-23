import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";
import { FullScreenSpinner } from "@/components/common/Spinner";

/**
 * Wraps /login and /register. Signed-in users are bounced to the
 * dashboard instead of seeing the login form again.
 */
export function PublicOnlyRoute() {
  const { isAuthenticated, isCheckingAuth } = useAuth();

  if (isCheckingAuth) {
    return <FullScreenSpinner />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
