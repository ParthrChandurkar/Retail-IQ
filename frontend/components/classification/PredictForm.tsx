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

const fields = [
  "entity_id",
  "total_price",
  "total_freight",
  "item_count",
  "product_count",
  "seller_count",
  "average_item_price",
  "maximum_item_price",
  "freight_ratio",
  "payment_value",
  "payment_installments",
  "delivery_days",
  "delivery_delay_hours",
  "is_late",
  "approval_hours",
  "carrier_handling_hours",
  "estimated_delivery_days",
  "shipping_limit_slack_days",
  "seller_distance_km",
  "average_product_weight_g",
  "average_product_volume_cm3",
  "customer_state",
  "seller_state",
  "dominant_category",
  "primary_payment_type",
  "purchase_month",
  "purchase_weekday",
  "purchase_hour",
] as const satisfies readonly (keyof PredictionRequest)[];
type MissingFields = Exclude<keyof PredictionRequest, (typeof fields)[number]>;
const schemaIsComplete: MissingFields extends never ? true : never = true;
const textFields = new Set<keyof PredictionRequest>([
  "entity_id",
  "customer_state",
  "seller_state",
  "dominant_category",
  "primary_payment_type",
]);
const required = new Set<keyof PredictionRequest>([
  "entity_id",
  "total_price",
  "total_freight",
  "item_count",
  "product_count",
  "seller_count",
  "average_item_price",
  "maximum_item_price",
  "customer_state",
  "seller_state",
  "dominant_category",
  "primary_payment_type",
  "purchase_month",
  "purchase_weekday",
  "purchase_hour",
]);

export function PredictForm() {
  void schemaIsComplete;
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PredictionRequest>();
  const prediction = useMutation({
    mutationFn: async (body: PredictionRequest) =>
      (
        await ClassificationService.predictApiV1ClassificationPredictPost({
          requestBody: body,
        })
      ).data,
  });
  const submit = handleSubmit((body) => prediction.mutate(body));
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-semibold">Single-record prediction</h2>
          <p className="mt-1 text-xs text-muted">
            Fields are compile-time bound to the generated OpenAPI
            PredictionRequest.
          </p>
        </div>
        <BrainCircuit className="text-primary" />
      </div>
      <form onSubmit={submit} className="mt-6">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {fields.map((field) => (
            <div key={field}>
              <Label htmlFor={`predict-${field}`}>
                {titleCase(field)}
                {required.has(field) ? " *" : ""}
              </Label>
              <Input
                id={`predict-${field}`}
                type={textFields.has(field) ? "text" : "number"}
                step={textFields.has(field) ? undefined : "any"}
                {...register(field, {
                  required: required.has(field),
                  setValueAs: textFields.has(field)
                    ? undefined
                    : (value: string) =>
                        value === "" ? undefined : Number(value),
                })}
              />
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
            Prediction failed. Validate every required field and its numeric
            range.
          </p>
        )}
        <Button className="mt-5" disabled={prediction.isPending}>
          {prediction.isPending ? "Scoring…" : "Predict satisfaction outcome"}
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
                prediction.data.predicted_label === "low_satisfaction"
                  ? "danger"
                  : "success"
              }
            >
              {Math.round(prediction.data.predicted_probability * 100)}%
              confident: {prediction.data.predicted_label.replace("_", " ")}
            </Badge>
          </div>
          <p className="mt-3 text-sm text-muted">
            This percentage is confidence in the displayed outcome—not a fixed
            probability of low satisfaction.
          </p>
        </div>
      )}
    </Card>
  );
}
