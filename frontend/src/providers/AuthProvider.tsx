"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { QUERY_KEYS, ROUTES } from "@/constants";
import { getMe, login as loginApi, signup as signupApi } from "@/services/auth.service";
import type { LoginRequest, SignupRequest, CurrentUserResponse } from "@/types/api";
import { queryClient } from "@/lib/query-client";

interface AuthContextValue {
  user: CurrentUserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("access_token");
    if (stored) setToken(stored);
    setIsReady(true);
  }, []);

  const {
    data: user,
    isLoading: userLoading,
  } = useQuery({
    queryKey: QUERY_KEYS.me,
    queryFn: getMe,
    enabled: !!token && isReady,
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: loginApi,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.me });
      router.push(ROUTES.dashboard);
    },
  });

  const signupMutation = useMutation({
    mutationFn: signupApi,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.me });
      router.push(ROUTES.dashboard);
    },
  });

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
    queryClient.clear();
    router.push(ROUTES.login);
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user: user ?? null,
        isLoading: !isReady || (!!token && userLoading),
        isAuthenticated: !!token && !!user,
        login: (data: LoginRequest) => loginMutation.mutateAsync(data).then(() => undefined),
        signup: (data: SignupRequest) => signupMutation.mutateAsync(data).then(() => undefined),
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
