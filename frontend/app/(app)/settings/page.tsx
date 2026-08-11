"use client";
import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Database, Moon, Sun, UserRound } from "lucide-react";
import { useTheme } from "next-themes";
import { AdminService } from "../../../src/generated/api";
import { PageHeader } from "../../../components/layout/PageHeader";
import { useAuth } from "../../../components/providers/AuthProvider";
import { Badge, Button, Card, ErrorState } from "../../../components/ui";
import { formatNumber, titleCase } from "../../../lib/utils";
export default function SettingsPage() {
  const { user } = useAuth();
  const { resolvedTheme, setTheme } = useTheme();
  const refresh = useQuery({
    queryKey: ["refresh-status"],
    queryFn: async () =>
      await AdminService.dataRefreshStatusApiV1AdminDataRefreshStatusGet(),
    enabled: user?.role === "admin",
  });
  const settings = useQuery({
    queryKey: ["admin-settings"],
    queryFn: async () => await AdminService.getSettingsApiV1AdminSettingsGet(),
    enabled: user?.role === "admin",
  });
  return (
    <>
      <PageHeader
        eyebrow="Workspace settings"
        title="Account & platform"
        description="Theme preference, authenticated account identity, and administrator data-pipeline status."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <UserRound className="text-primary" />
          <h2 className="mt-5 font-semibold">Account</h2>
          <dl className="mt-5 space-y-3 text-sm">
            <div className="flex justify-between border-b pb-3">
              <dt className="text-muted">Email</dt>
              <dd>{user?.email}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted">Role</dt>
              <dd>
                <Badge>{titleCase(user?.role ?? "")}</Badge>
              </dd>
            </div>
          </dl>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">Appearance</h2>
              <p className="mt-1 text-sm text-muted">
                Both palettes use the binding design tokens.
              </p>
            </div>
            {resolvedTheme === "dark" ? (
              <Moon className="text-primary" />
            ) : (
              <Sun className="text-accent" />
            )}
          </div>
          <div className="mt-6 flex gap-2">
            <Button
              variant={resolvedTheme === "light" ? "primary" : "secondary"}
              onClick={() => setTheme("light")}
            >
              <Sun className="h-4 w-4" /> Light
            </Button>
            <Button
              variant={resolvedTheme === "dark" ? "primary" : "secondary"}
              onClick={() => setTheme("dark")}
            >
              <Moon className="h-4 w-4" /> Dark
            </Button>
          </div>
        </Card>
        {user?.role === "admin" && (
          <Card className="lg:col-span-2">
            <Database className="text-primary" />
            <h2 className="mt-5 font-semibold">Latest data refresh</h2>
            {refresh.error ? (
              <ErrorState error={refresh.error} />
            ) : refresh.data ? (
              <dl className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <Stat label="Job" value={refresh.data.data.job_name} />
                <Stat label="Status" value={refresh.data.data.status} />
                <Stat
                  label="Rows affected"
                  value={formatNumber(refresh.data.data.rows_affected ?? 0)}
                />
                <Stat
                  label="Finished"
                  value={
                    refresh.data.data.finished_at
                      ? new Date(refresh.data.data.finished_at).toLocaleString()
                      : "In progress"
                  }
                />
              </dl>
            ) : (
              <p className="mt-3 text-sm text-muted">Loading refresh status…</p>
            )}
            {settings.data && (
              <p className="mt-5 flex items-center gap-2 text-xs text-muted">
                <CheckCircle2 className="h-4 w-4 text-success" />{" "}
                {Object.keys(settings.data.data.settings).length} governed
                administrator settings loaded.
              </p>
            )}
          </Card>
        )}
      </div>
    </>
  );
}
function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-control border bg-background p-4">
      <dt className="text-xs uppercase tracking-wide text-muted">{label}</dt>
      <dd className="mt-2 font-mono text-sm">{value}</dd>
    </div>
  );
}
