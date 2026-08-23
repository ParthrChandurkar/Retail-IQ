import { ArrowLeft, Database, Layers3, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { Button, Card } from "../../../components/ui";
export default function OverviewPage() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-5 py-10">
      <Button asChild variant="ghost">
        <Link href="/">
          <ArrowLeft className="h-4 w-4" /> Back
        </Link>
      </Button>
      <header className="py-14">
        <p className="text-xs font-bold uppercase tracking-[.18em] text-primary">
          Project overview
        </p>
        <h1 className="mt-3 max-w-4xl text-4xl font-semibold tracking-tight sm:text-6xl">
          Analytics first. Machine learning where it adds business value.
        </h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-muted">
          Built on Indian Store Data, the platform follows the complete
          data-science workflow from source understanding and cleaning through
          statistical analysis, customer intelligence, model governance,
          dashboards, and recommendations across five years of orders.
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <Database className="text-primary" />
          <h2 className="mt-5 font-semibold">Verified Indian retail data</h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            One verified 100,000-row source is integrated into raw, curated,
            marts, and ML PostgreSQL schemas without fabricating business
            values.
          </p>
        </Card>
        <Card>
          <Layers3 className="text-primary" />
          <h2 className="mt-5 font-semibold">Clean architecture</h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            Next.js consumes a typed FastAPI contract; analytics and ML remain
            sibling services behind the API.
          </p>
        </Card>
        <Card>
          <ShieldCheck className="text-primary" />
          <h2 className="mt-5 font-semibold">Governed evidence</h2>
          <p className="mt-2 text-sm leading-6 text-muted">
            Every metric follows shared definitions, every statistical result
            carries a conclusion, and model probability means confidence in its
            displayed outcome.
          </p>
        </Card>
      </div>
      <Card className="mt-4">
        <h2 className="font-semibold">System flow</h2>
        <div className="mt-5 flex flex-wrap items-center gap-2 text-sm">
          {[
            "Indian Store Data CSV",
            "Raw fidelity",
            "Curated quality",
            "Analytics marts",
            "FastAPI",
            "Next.js dashboards",
            "Business decisions",
          ].map((item, index) => (
            <span key={item} className="flex items-center gap-2">
              <span className="rounded-control border bg-background px-3 py-2">
                {item}
              </span>
              {index < 6 && <span className="text-muted">→</span>}
            </span>
          ))}
        </div>
      </Card>
      <div className="mt-8">
        <Button asChild>
          <Link href="/login">Continue to secure workspace</Link>
        </Button>
      </div>
    </main>
  );
}
