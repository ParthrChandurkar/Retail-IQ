"use client";

import { useMutation } from "@tanstack/react-query";
import { BrainCircuit } from "lucide-react";
import { useForm } from "react-hook-form";
import {
  ClassificationService,
  type PredictionRequest,
} from "../../src/generated/api";
import { titleCase } from "../../lib/utils";
import { Badge, Button, Card, Input, Label } from "../ui";

const featureFields = [
  "sales",
  "discount_pct",
  "category",
  "sub_category",
  "segment",
  "city_type",
  "state",
  "region",
  "order_month",
  "order_dow",
] as const satisfies readonly (keyof PredictionRequest)[];
type MissingFields = Exclude<
  keyof PredictionRequest,
  "entity_id" | (typeof featureFields)[number]
>;
const featureSchemaIsComplete: MissingFields extends never ? true : never =
  true;
const numericFields = new Set<keyof PredictionRequest>([
  "sales",
  "discount_pct",
  "order_month",
  "order_dow",
]);
const choices: Partial<Record<keyof PredictionRequest, readonly string[]>> = {
  segment: ["Consumer", "Corporate"],
  city_type: ["Tier 1", "Tier 2", "Village"],
  region: ["North", "South", "East", "West"],
};

export function PredictForm() {
  void featureSchemaIsComplete;
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PredictionRequest>({
    defaultValues: {
      entity_id: "dashboard-order",
      sales: 46837.74,
      discount_pct: 14,
      category: "Sessional Fruits & Vegetables",
      sub_category: "Carrots",
      segment: "Corporate",
      city_type: "Tier 2",
      state: "Tamil Nadu",
      region: "South",
      order_month: 7,
      order_dow: 7,
    },
  });
  const prediction = useMutation({
    mutationFn: async (body: PredictionRequest) =>
      (
        await ClassificationService.predictApiV1ClassificationPredictPost({
          requestBody: body,
        })
      ).data,
  });
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-semibold">Single-order prediction</h2>
          <p className="mt-1 text-xs text-muted">
            Ten checkout features are compile-time bound to the generated M7
            OpenAPI client. The audit identifier is metadata, not a model
            feature.
          </p>
        </div>
        <BrainCircuit className="text-primary" />
      </div>
      <form
        onSubmit={handleSubmit((body) => prediction.mutate(body))}
        className="mt-6"
      >
        <div className="mb-3 max-w-sm">
          <Label htmlFor="predict-entity_id">Audit identifier *</Label>
          <Input
            id="predict-entity_id"
            {...register("entity_id", { required: true })}
          />
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {featureFields.map((field) => (
            <div key={field}>
              <Label htmlFor={`predict-${field}`}>{titleCase(field)} *</Label>
              {choices[field] ? (
                <select
                  id={`predict-${field}`}
                  className="min-h-10 w-full rounded-control border bg-background px-3 text-sm text-ink focus:border-primary"
                  {...register(field, { required: true })}
                >
                  {choices[field]!.map((choice) => (
                    <option key={choice}>{choice}</option>
                  ))}
                </select>
              ) : (
                <Input
                  id={`predict-${field}`}
                  type={numericFields.has(field) ? "number" : "text"}
                  step={numericFields.has(field) ? "any" : undefined}
                  min={
                    field === "order_month" || field === "order_dow"
                      ? 1
                      : undefined
                  }
                  max={
                    field === "order_month"
                      ? 12
                      : field === "order_dow"
                        ? 7
                        : undefined
                  }
                  {...register(field, {
                    required: true,
                    setValueAs: numericFields.has(field)
                      ? (value: string) => Number(value)
                      : undefined,
                  })}
                />
              )}
              {errors[field] && (
                <p className="mt-1 text-xs text-danger">
                  Required by the live schema
                </p>
              )}
            </div>
          ))}
        </div>
        {prediction.error && (
          <p role="alert" className="mt-4 text-sm text-danger">
            Prediction failed. Check every checkout value and try again.
          </p>
        )}
        <Button className="mt-5" disabled={prediction.isPending}>
          {prediction.isPending ? "Scoring…" : "Predict profit outcome"}
        </Button>
      </form>
      {prediction.data && (
        <div
          className="mt-6 rounded-card border bg-background p-5"
          aria-live="polite"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted">
                Predicted outcome
              </p>
              <p className="mt-2 text-2xl font-semibold">
                {titleCase(prediction.data.predicted_label)}
              </p>
            </div>
            <Badge
              tone={
                prediction.data.predicted_label === "high_profit_order"
                  ? "success"
                  : "neutral"
              }
            >
              {Math.round(prediction.data.predicted_probability * 100)}%
              confident: {prediction.data.predicted_label}
            </Badge>
          </div>
          <p className="mt-3 text-sm text-muted">
            Confidence is for the displayed outcome: P(high-profit) when
            high-profit is predicted, otherwise 1 − P(high-profit).
          </p>
        </div>
      )}
    </Card>
  );
}
