"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useAuth } from "../../../components/providers/AuthProvider";
import { Button, Card, Input, Label } from "../../../components/ui";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});
type Form = z.infer<typeof schema>;

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="grid min-h-screen place-items-center text-sm text-muted">
          Loading secure sign-in…
        </main>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const search = useSearchParams();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<Form>({ resolver: zodResolver(schema) });
  const submit = handleSubmit(async (values) => {
    try {
      await login(values.email, values.password);
      router.replace(search.get("next") ?? "/dashboard");
    } catch {
      setError("root", {
        message:
          "Sign-in failed. Check your administrator-provided credentials.",
      });
    }
  });
  return (
    <main className="grid min-h-screen place-items-center px-5 py-12">
      <Card className="w-full max-w-md p-7 sm:p-9">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-2 text-sm text-muted"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Retail IQ
        </Link>
        <span className="grid h-11 w-11 place-items-center rounded-control bg-primary/10 text-primary">
          <LockKeyhole />
        </span>
        <h1 className="mt-5 text-3xl font-semibold tracking-tight">
          Welcome back
        </h1>
        <p className="mt-2 text-sm text-muted">
          Sign in to the governed analytics workspace.
        </p>
        <form className="mt-8 space-y-5" onSubmit={submit}>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="username"
              {...register("email")}
            />
            {errors.email && (
              <p className="mt-1 text-xs text-danger">{errors.email.message}</p>
            )}
          </div>
          <div>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register("password")}
            />
            {errors.password && (
              <p className="mt-1 text-xs text-danger">
                {errors.password.message}
              </p>
            )}
          </div>
          {errors.root && (
            <p role="alert" className="text-sm text-danger">
              {errors.root.message}
            </p>
          )}
          <Button className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Signing in…" : "Sign in securely"}
          </Button>
        </form>
        <p className="mt-6 text-xs leading-5 text-muted">
          Access tokens are held in memory only. Session renewal uses the
          backend’s httpOnly, Secure, SameSite=Strict refresh cookie.
        </p>
      </Card>
    </main>
  );
}
