import { create } from "zustand";
import type { UserResponse } from "@/types/api";

interface AuthState {
  user: UserResponse | null;
  isLoading: boolean;           // true while /auth/me is in-flight on app start
  isAuthenticated: boolean;
  setUser: (user: UserResponse | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  setUser: (user) =>
    set({ user, isAuthenticated: user !== null, isLoading: false }),

  setLoading: (isLoading) => set({ isLoading }),

  logout: () =>
    set({ user: null, isAuthenticated: false, isLoading: false }),
}));
