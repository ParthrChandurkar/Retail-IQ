"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  BarChart3,
  Boxes,
  BrainCircuit,
  ChevronLeft,
  CircleDollarSign,
  Globe2,
  Home,
  Lightbulb,
  Menu,
  Settings,
  ShoppingBag,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { create } from "zustand";
import { useAuth } from "../providers/AuthProvider";
import { Button, Skeleton } from "../ui";
import { FilterBar } from "../filters/FilterBar";
import { Topbar } from "./Topbar";
import { cn } from "../../lib/utils";

const links = [
  ["Overview", "/dashboard", Home],
  ["Sales", "/dashboard/sales", CircleDollarSign],
  ["Customers", "/dashboard/customers", Users],
  ["Products", "/dashboard/products", ShoppingBag],
  ["Regional", "/dashboard/regional", Globe2],
  ["Classification", "/dashboard/classification", BrainCircuit],
  ["Analytics", "/dashboard/analytics", BarChart3],
  ["Insights", "/dashboard/insights", Lightbulb],
  ["Settings", "/settings", Settings],
] as const;
const useShell = create<{ collapsed: boolean; toggle: () => void }>((set) => ({
  collapsed: false,
  toggle: () => set((s) => ({ collapsed: !s.collapsed })),
}));

export function AppShell({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const { collapsed, toggle } = useShell();
  const [mobile, setMobile] = useState(false);
  useEffect(() => {
    if (ready && !user)
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
  }, [ready, user, router, pathname]);
  if (!ready || !user)
    return (
      <main className="grid min-h-screen place-items-center">
        <div className="w-72 space-y-3">
          <Skeleton className="h-12" />
          <Skeleton className="h-4" />
          <p className="text-center text-sm text-muted">
            Restoring secure session…
          </p>
        </div>
      </main>
    );
  return (
    <div className="min-h-screen bg-background">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 hidden border-r bg-surface transition-[width] lg:block",
          collapsed ? "w-16" : "w-60",
        )}
      >
        <Sidebar
          collapsed={collapsed}
          pathname={pathname}
          onNavigate={() => undefined}
        />
        <Button
          variant="ghost"
          className="absolute -right-4 top-20 h-8 min-h-8 w-8 rounded-full border bg-background p-0"
          onClick={toggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <ChevronLeft
            className={cn("h-4 w-4 transition", collapsed && "rotate-180")}
          />
        </Button>
      </aside>
      <AnimatePresence>
        {mobile && (
          <motion.aside
            initial={{ x: -260 }}
            animate={{ x: 0 }}
            exit={{ x: -260 }}
            className="fixed inset-y-0 left-0 z-50 w-72 border-r bg-surface lg:hidden"
          >
            <Button
              variant="ghost"
              className="absolute right-3 top-3 p-2"
              onClick={() => setMobile(false)}
              aria-label="Close navigation"
            >
              <X />
            </Button>
            <Sidebar
              collapsed={false}
              pathname={pathname}
              onNavigate={() => setMobile(false)}
            />
          </motion.aside>
        )}
      </AnimatePresence>
      <div
        className={cn(
          "transition-[padding]",
          collapsed ? "lg:pl-16" : "lg:pl-60",
        )}
      >
        <Topbar onMenu={() => setMobile(true)} />
        <FilterBar />
        <motion.main
          key={pathname}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.18 }}
          className="mx-auto max-w-[1600px] p-4 sm:p-6 lg:p-8"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}
function Sidebar({
  collapsed,
  pathname,
  onNavigate,
}: {
  collapsed: boolean;
  pathname: string;
  onNavigate: () => void;
}) {
  return (
    <div className="flex h-full flex-col p-3">
      <Link href="/" className="mb-6 flex h-12 items-center gap-3 px-2">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-control bg-primary text-[var(--primary-foreground)]">
          <Boxes className="h-5 w-5" />
        </span>
        {!collapsed && (
          <span>
            <strong className="block leading-none">Retail IQ</strong>
            <small className="text-muted">Business Intelligence</small>
          </span>
        )}
      </Link>
      <nav aria-label="Dashboard navigation" className="space-y-1">
        {links.map(([label, href, Icon]) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              onClick={onNavigate}
              title={collapsed ? label : undefined}
              className={cn(
                "flex h-10 items-center gap-3 rounded-control px-3 text-sm font-medium text-muted transition hover:bg-background hover:text-ink",
                active && "bg-background text-primary",
              )}
            >
              <Icon className="h-[18px] w-[18px] shrink-0" />
              {!collapsed && label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
export function MobileMenuButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      variant="ghost"
      className="p-2 lg:hidden"
      onClick={onClick}
      aria-label="Open navigation"
    >
      <Menu />
    </Button>
  );
}
