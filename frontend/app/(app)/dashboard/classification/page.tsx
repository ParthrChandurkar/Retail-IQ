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
    queryFn: async () =>
      await ClassificationService.modelInfoApiV1ClassificationModelInfoGet(),
  });
  const metrics = useQuery({
    queryKey: ["model-metrics"],
    queryFn: async () =>
      await ClassificationService.modelMetricsApiV1ClassificationMetricsGet(),
  });
  const features = useQuery({
    queryKey: ["feature-importance"],
    queryFn: async () =>
      await ClassificationService.featureImportanceApiV1ClassificationFeatureImportanceGet(),
  });
  const failed = [info, metrics, features].find((q) => q.error);
  if (failed) return <ErrorState error={failed.error} />;
  if (!info.data || !metrics.data || !features.data) return null;
  const m = metrics.data.data;
  return (
    <>
      <PageHeader
        eyebrow="Model governance"
        title="Satisfaction classification"
        description={`${info.data.data.algorithm}, model ${info.data.data.model_id}. Positive-class metrics below refer specifically to low_satisfaction.`}
      />
      <KPIGrid>
        <KPICard
          label="Accuracy"
          value={formatPercent(m.accuracy * 100, 2)}
          icon={Target}
        />
        <KPICard
          label="Precision · low"
          value={formatPercent(m.precision_low_satisfaction * 100, 2)}
          icon={Crosshair}
        />
        <KPICard
          label="Recall · low"
          value={formatPercent(m.recall_low_satisfaction * 100, 2)}
          icon={Activity}
        />
        <KPICard
          label="F1 · low"
          value={formatPercent(m.f1_low_satisfaction * 100, 2)}
          detail={`ROC-AUC ${m.roc_auc.toFixed(4)}`}
          icon={Gauge}
        />
      </KPIGrid>
      <div className="grid gap-4 xl:grid-cols-2">
        <ConfusionMatrix matrix={m.confusion_matrix} />
        <FeatureImportanceBar data={features.data.data} />
        <div className="xl:col-span-2">
          <PredictForm />
        </div>
      </div>
    </>
  );
}
