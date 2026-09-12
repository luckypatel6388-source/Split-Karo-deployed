import { useEffect } from "react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppRouter } from "@/router";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/api/auth";
import { ApiRequestError } from "@/api/client";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,        // 30 s
      retry: (failureCount, error) => {
        // Don't retry 401/403/404 — they are definitive
        if (error instanceof ApiRequestError) {
          if ([401, 403, 404].includes(error.status)) return false;
        }
        return failureCount < 2;
      },
    },
  },
});

/**
 * On app start, call GET /auth/me to restore the session from the cookie.
 * Sets isLoading=false once resolved regardless of outcome.
 */
function AuthBootstrap() {
  const { setUser, setLoading } = useAuthStore();

  useEffect(() => {
    authApi
      .me()
      .then((user) => setUser(user))
      .catch(() => {
        // 401 = no valid session — stay on login
        setLoading(false);
      });
  }, [setUser, setLoading]);

  return null;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthBootstrap />
        <AppRouter />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
