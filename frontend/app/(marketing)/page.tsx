import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Database,
  LineChart,
} from "lucide-react";
import Link from "next/link";
import { Button, Card } from "../../components/ui";

const capabilities = [
  [
    BarChart3,
    "Business intelligence",
    "Revenue, profit, discount, customer-segment, category, and trusted regional analysis from governed marts.",
  ],
  [
    LineChart,
    "Statistical evidence",
    "Descriptive statistics, correlations, covariance, and hypothesis tests translated into business language.",
  ],
  [
    BrainCircuit,
    "Decision support",
    "A registered high-profit order classifier and deterministic recommendations support operational action.",
  ],
];
export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-background">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="grid h-9 w-9 place-items-center rounded-control bg-primary text-[var(--primary-foreground)]">
            <Database className="h-5 w-5" />
          </span>
          Retail IQ
        </Link>
        <div className="flex gap-2">
          <Button asChild variant="ghost">
            <Link href="/overview">Project overview</Link>
          </Button>
          <Button asChild>
            <Link href="/login">Sign in</Link>
          </Button>
        </div>
      </nav>
      <section className="relative mx-auto grid min-h-[68vh] max-w-7xl items-center gap-12 px-5 py-16 lg:grid-cols-[1.1fr_.9fr]">
        <div>
          <p className="mb-5 text-xs font-bold uppercase tracking-[.2em] text-primary">
            Retail Business Intelligence
          </p>
          <h1 className="max-w-4xl text-5xl font-semibold leading-[.95] tracking-[-.055em] sm:text-7xl">
            Turn retail operations into clear decisions.
          </h1>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-muted">
            Retail IQ unifies governed commerce data, customer analytics,
            statistical evidence, and responsible machine learning in one
            production-grade decision platform.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild className="px-5">
              <Link href="/login">
                Open analytics workspace <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="secondary">
              <Link href="/overview">Explore the methodology</Link>
            </Button>
          </div>
        </div>
        <Card className="relative overflow-hidden p-0">
          <div className="border-b p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">
                Intelligence pipeline
              </span>
              <span className="rounded-full bg-success/10 px-2 py-1 text-xs font-semibold text-success">
                Live
              </span>
            </div>
          </div>
          <div className="space-y-3 p-5">
            {[
              "Single-source ingestion",
              "Curated quality layer",
              "Pre-aggregated BI marts",
              "Analytics & statistics",
              "High-profit order model",
              "Decision dashboards",
            ].map((item, index) => (
              <div
                key={item}
                className="flex items-center gap-4 rounded-control border bg-background p-3"
              >
                <span className="grid h-7 w-7 place-items-center rounded-full bg-primary/10 font-mono text-xs font-bold text-primary">
                  {index + 1}
                </span>
                <span className="text-sm font-medium">{item}</span>
              </div>
            ))}
          </div>
        </Card>
      </section>
      <section className="mx-auto grid max-w-7xl gap-4 px-5 pb-20 md:grid-cols-3">
        {capabilities.map(([Icon, title, copy]) => (
          <Card key={String(title)} className="p-6">
            <Icon className="mb-5 h-6 w-6 text-primary" />
            <h2 className="font-semibold">{String(title)}</h2>
            <p className="mt-2 text-sm leading-6 text-muted">{String(copy)}</p>
          </Card>
        ))}
      </section>
    </main>
  );
}
