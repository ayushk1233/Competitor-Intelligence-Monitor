"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { ROUTES } from "@/constants";
import { signupSchema, type SignupFormValues } from "@/lib/schemas";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Eye, EyeOff } from "lucide-react";
import type { AxiosError } from "axios";
import type { ApiError } from "@/types/api";

export default function SignupPage() {
  const { signup } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
  });

  async function onSubmit(data: SignupFormValues) {
    setServerError(null);
    try {
      await signup({
        email: data.email,
        password: data.password,
        display_name: data.display_name || undefined,
      });
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
      <h1 className="text-2xl font-bold tracking-tight text-white">Create your account</h1>
      <p className="mt-1 text-sm text-[#A3A3A3]">Start monitoring your competitive landscape</p>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5">
        {serverError && (
          <div className="rounded-lg bg-[#EF4444]/10 px-4 py-3 text-sm text-[#EF4444]">
            {serverError}
          </div>
        )}

        <div className="space-y-2">
          <label htmlFor="display_name" className="block text-xs font-semibold uppercase tracking-wider text-[#A3A3A3]">
            Display name <span className="text-neutral-500">(optional)</span>
          </label>
          <Input
            id="display_name"
            type="text"
            placeholder="Your name"
            className="w-full rounded-lg border border-border bg-card p-3 text-sm text-white placeholder:text-neutral-500 focus:border-[#BC6C50] focus:outline-none focus:ring-0"
            {...register("display_name")}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-wider text-[#A3A3A3]">
            Email
          </label>
          <Input
            id="email"
            type="email"
            placeholder="you@example.com"
            className="w-full rounded-lg border border-border bg-card p-3 text-sm text-white placeholder:text-neutral-500 focus:border-[#BC6C50] focus:outline-none focus:ring-0"
            {...register("email")}
          />
          {errors.email && (
            <p className="text-xs text-[#EF4444]">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wider text-[#A3A3A3]">
            Password
          </label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="At least 6 characters"
              className="w-full rounded-lg border border-border bg-card p-3 pr-10 text-sm text-white placeholder:text-neutral-500 focus:border-[#BC6C50] focus:outline-none focus:ring-0"
              {...register("password")}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#A3A3A3] hover:text-white"
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
          className="w-full rounded-lg border border-[#BC6C50] bg-transparent text-sm font-medium text-[#BC6C50] transition-all hover:bg-[#BC6C50]/10"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating account...
            </>
          ) : (
            "Create account \u2192"
          )}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[#A3A3A3]">
        Already have an account?{" "}
        <Link href={ROUTES.login} className="font-medium text-[#BC6C50] hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
