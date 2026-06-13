"use client";

import { useMutation } from "@tanstack/react-query";
import type { LoginRequest, SignupRequest } from "@/types/api";
import { useAuth as useAuthContext } from "@/providers/AuthProvider";
import { login as loginApi, signup as signupApi } from "@/services/auth.service";

export function useAuth() {
  return useAuthContext();
}

export function useLoginMutation() {
  const { login } = useAuthContext();
  return useMutation({
    mutationFn: (data: LoginRequest) => login(data),
  });
}

export function useSignupMutation() {
  const { signup } = useAuthContext();
  return useMutation({
    mutationFn: (data: SignupRequest) => signup(data),
  });
}
