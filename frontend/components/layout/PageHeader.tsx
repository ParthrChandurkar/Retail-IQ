import type { ReactNode } from "react";
export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <header className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <p className="mb-2 text-xs font-bold uppercase tracking-[.16em] text-primary">
          {eyebrow}
        </p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          {title}
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
          {description}
        </p>
      </div>
      {action}
    </header>
  );
}
export function Freshness({ value }: { value?: string }) {
  if (!value) return null;
  return (
    <p className="mt-3 text-xs text-muted">
      Data generated {new Date(value).toLocaleString()}
    </p>
  );
}
