import { Slot } from "@radix-ui/react-slot";
import {
  forwardRef,
  type ButtonHTMLAttributes,
  type HTMLAttributes,
  type InputHTMLAttributes,
  type ReactNode,
} from "react";
import { cn } from "../../lib/utils";

export const Button = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement> & {
    asChild?: boolean;
    variant?: "primary" | "secondary" | "ghost";
  }
>(({ className, asChild, variant = "primary", ...props }, ref) => {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      ref={ref}
      className={cn(
        "inline-flex min-h-10 items-center justify-center gap-2 rounded-control px-4 text-sm font-semibold transition hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "bg-primary text-[var(--primary-foreground)]",
        variant === "secondary" && "border bg-surface text-ink",
        variant === "ghost" && "text-muted hover:bg-surface hover:text-ink",
        className,
      )}
      {...props}
    />
  );
});
Button.displayName = "Button";
export const Card = ({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) => (
  <section
    className={cn("rounded-card border bg-surface p-5", className)}
    {...props}
  />
);
export const Input = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "min-h-10 w-full rounded-control border bg-background px-3 text-sm text-ink placeholder:text-muted focus:border-primary",
      className,
    )}
    {...props}
  />
));
Input.displayName = "Input";
export function Label({
  children,
  htmlFor,
}: {
  children: ReactNode;
  htmlFor?: string;
}) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-muted"
    >
      {children}
    </label>
  );
}
export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "success" | "danger" | "accent";
}) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold",
        tone === "success" && "border-success/30 bg-success/10 text-success",
        tone === "danger" && "border-danger/30 bg-danger/10 text-danger",
        tone === "accent" && "border-accent/30 bg-accent/10 text-accent",
      )}
    >
      {children}
    </span>
  );
}
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse rounded-card bg-border/60", className)}
      aria-hidden="true"
    />
  );
}
export function ErrorState({ error }: { error: unknown }) {
  return (
    <Card role="alert" className="border-danger/40">
      <p className="font-semibold text-danger">Unable to load this view</p>
      <p className="mt-1 text-sm text-muted">
        {error instanceof Error ? error.message : "The API request failed."}
      </p>
    </Card>
  );
}
