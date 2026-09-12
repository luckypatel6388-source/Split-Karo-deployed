import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { FullPageSpinner } from "@/components/shared/LoadingSpinner";

/**
 * Protects routes that require authentication.
 * While the session is being verified (isLoading=true) → spinner.
 * Not authenticated → redirect to /login.
 * Authenticated → render child routes.
 */
export function AuthGuard() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) return <FullPageSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return <Outlet />;
}

/**
 * Redirects already-authenticated users away from /login and /register.
 */
export function GuestGuard() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) return <FullPageSpinner />;
  if (isAuthenticated) return <Navigate to="/" replace />;

  return <Outlet />;
}
