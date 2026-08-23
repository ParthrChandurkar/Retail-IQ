"use client";

import { LogOut, Menu, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useRouter } from "next/navigation";
import { useEffect, useState, type Ref } from "react";
import { useAuth } from "../providers/AuthProvider";
import { Button } from "../ui";

export function Topbar({
  onMenu,
  menuButtonRef,
}: {
  onMenu: () => void;
  menuButtonRef?: Ref<HTMLButtonElement>;
}) {
  const { resolvedTheme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b bg-[color:color-mix(in_srgb,var(--background)_88%,transparent)] px-4 backdrop-blur sm:px-6">
      <div className="flex items-center gap-2">
        <Button
          ref={menuButtonRef}
          variant="ghost"
          className="p-2 lg:hidden"
          onClick={onMenu}
          aria-label="Open navigation"
        >
          <Menu />
        </Button>
        <span className="hidden text-sm text-muted sm:inline">
          Live commerce intelligence
        </span>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          className="p-2"
          onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
          aria-label="Toggle color theme"
        >
          {mounted && resolvedTheme === "dark" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>
        <div className="hidden text-right sm:block">
          <p className="text-xs font-semibold">
            {user?.full_name ?? user?.email}
          </p>
          <p className="text-[11px] uppercase tracking-wide text-muted">
            {user?.role}
          </p>
        </div>
        <Button
          variant="ghost"
          className="p-2"
          onClick={() => {
            logout();
            router.replace("/login");
          }}
          aria-label="Sign out"
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
