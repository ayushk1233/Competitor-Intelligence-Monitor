import { apiClient } from "@/lib/api-client";
import type {
  SignupRequest,
  LoginRequest,
  AuthResponse,
  CurrentUserResponse,
} from "@/types/api";

export async function signup(data: SignupRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>("/api/auth/signup", data);
  return response.data;
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>("/api/auth/login", data);
  return response.data;
}

export async function getMe(): Promise<CurrentUserResponse> {
  const response = await apiClient.get<CurrentUserResponse>("/api/auth/me");
  return response.data;
}
