import { Card } from "../ui";
import { titleCase } from "../../lib/utils";
export function CorrelationHeatmap({
  fields,
  matrix,
}: {
  fields: string[];
  matrix: Record<string, Record<string, number>>;
}) {
  return (
    <Card className="overflow-hidden">
      <h2 className="font-semibold">Pearson correlation matrix</h2>
      <p className="mt-1 text-xs text-muted">
        Color intensity represents absolute association; sign is printed in each
        cell.
      </p>
      <div className="mt-5 overflow-auto">
        <div
          className="grid min-w-[720px]"
          style={{
            gridTemplateColumns: `10rem repeat(${fields.length}, minmax(4rem,1fr))`,
          }}
        >
          <span />
          {fields.map((f) => (
            <span
              key={f}
              className="rotate-[-25deg] px-1 py-3 text-center text-[10px] text-muted"
            >
              {titleCase(f)}
            </span>
          ))}
          {fields.flatMap((row) => [
            <strong
              key={`${row}-label`}
              className="flex items-center border-t pr-3 text-xs"
            >
              {titleCase(row)}
            </strong>,
            ...fields.map((col) => {
              const value = Number(matrix[row]?.[col] ?? 0);
              const alpha = Math.max(0.06, Math.abs(value) * 0.7);
              return (
                <span
                  key={`${row}-${col}`}
                  className="grid min-h-14 place-items-center border-l border-t font-mono text-xs"
                  style={{
                    background: `color-mix(in srgb, ${value < 0 ? "var(--danger)" : "var(--primary)"} ${alpha * 100}%, transparent)`,
                  }}
                >
                  {value.toFixed(2)}
                </span>
              );
            }),
          ])}
        </div>
      </div>
    </Card>
  );
}
