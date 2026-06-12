"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { ROUTES } from "@/constants";
import { loginSchema, type LoginFormValues } from "@/lib/schemas";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Eye, EyeOff } from "lucide-react";
import type { AxiosError } from "axios";
import type { ApiError } from "@/types/api";

export default function LoginPage() {
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(data: LoginFormValues) {
    setServerError(null);
    try {
      await login({ email: data.email, password: data.password });
    } catch (err) {
      const axiosErr = err as AxiosError<ApiError>;
      const detail = axiosErr.response?.data?.detail;
      if (detail) {
        setServerError(detail);
      } else {
        setServerError("Network error. Please check your connection.");
      }
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight font-mono text-foreground">Sign in to CIM</h1>
      <p className="mt-1 text-sm text-muted-foreground">Monitor your competitive landscape</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5">
        {serverError && (
          <div className="rounded-lg bg-[#EF4444]/10 px-4 py-3 text-sm text-[#EF4444]">
            {serverError}
          </div>
        )}

        <div className="space-y-2">
          <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-wider font-mono text-muted-foreground">
            Email
          </label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            className="w-full rounded-lg border border-border bg-card p-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-[var(--orange)] focus:outline-none focus:ring-0"
            {...register("email")}
          />
          {errors.email && (
            <p className="text-xs text-[#EF4444]">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wider font-mono text-muted-foreground">
            Password
          </label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              className="w-full rounded-lg border border-border bg-card p-3 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:border-[var(--orange)] focus:outline-none focus:ring-0"
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="text-xs text-[#EF4444]">{errors.password.message}</p>
          )}
        </div>

        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg border border-[var(--orange)] bg-transparent text-sm font-medium font-mono text-[var(--orange)] transition-all hover:bg-[var(--orange)]/10"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Signing in...
            </>
          ) : (
            "Sign in \u2192"
          )}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        No account?{" "}
        <Link href={ROUTES.signup} className="font-medium text-[var(--orange)] hover:underline">
          Start 14-day free trial
        </Link>
      </p>
    </div>
  );
}
