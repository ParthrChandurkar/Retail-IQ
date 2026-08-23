"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, Crosshair, Gauge, Target } from "lucide-react";
import { ClassificationService } from "../../../../src/generated/api";
import { ConfusionMatrix } from "../../../../components/charts/ConfusionMatrix";
import { FeatureImportanceBar } from "../../../../components/charts/Charts";
import { PredictForm } from "../../../../components/classification/PredictForm";
import { KPIGrid, KPICard } from "../../../../components/kpi/KPI";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import { formatPercent } from "../../../../lib/utils";

export default function ClassificationPage() {
  const info = useQuery({
    queryKey: ["model-info"],
    queryFn: () =>
      ClassificationService.modelInfoApiV1ClassificationModelInfoGet(),
  });
  const metrics = useQuery({
    queryKey: ["model-metrics"],
    queryFn: () =>
      ClassificationService.modelMetricsApiV1ClassificationMetricsGet(),
  });
  const features = useQuery({
    queryKey: ["feature-importance"],
    queryFn: () =>
      ClassificationService.featureImportanceApiV1ClassificationFeatureImportanceGet(),
  });
  const failed = [info, metrics, features].find((query) => query.error);
  if (failed) return <ErrorState error={failed.error} />;
  if (!info.data || !metrics.data || !features.data) return null;
  const model = info.data.data;
  const metric = metrics.data.data;
  return (
    <>
      <PageHeader
        eyebrow="Model governance"
        title="High-profit order classification"
        description={`${model.algorithm}, model ${model.model_id}. Precision, recall, and F1 refer specifically to high_profit_order.`}
      />
      <KPIGrid>
        <KPICard
          label="Accuracy"
          value={formatPercent(metric.accuracy * 100, 2)}
          icon={Target}
        />
        <KPICard
          label="Precision · high profit"
          value={formatPercent(metric.precision_high_profit_order * 100, 2)}
          icon={Crosshair}
        />
        <KPICard
          label="Recall · high profit"
          value={formatPercent(metric.recall_high_profit_order * 100, 2)}
          icon={Activity}
        />
        <KPICard
          label="F1 · high profit"
          value={formatPercent(metric.f1_high_profit_order * 100, 2)}
          detail={`ROC-AUC ${metric.roc_auc.toFixed(4)}`}
          icon={Gauge}
        />
      </KPIGrid>
      <div className="grid gap-4 xl:grid-cols-2">
        <ConfusionMatrix matrix={metric.confusion_matrix} />
        <FeatureImportanceBar data={features.data.data} />
        <div className="xl:col-span-2">
          <PredictForm />
        </div>
      </div>
    </>
  );
}
