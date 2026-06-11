import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import type { AxiosError } from "axios";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function extractApiError(error: unknown): string {
  const axiosError = error as AxiosError<{ detail: string }>;
  if (axiosError.response?.data?.detail) {
    return axiosError.response.data.detail;
  }
  if (axiosError.message) {
    return axiosError.message;
  }
  return "An unexpected error occurred";
}
