"use client";
import { useQuery } from "@tanstack/react-query";
import {
  RecommendationsService,
  ReviewsService,
} from "../../../../src/generated/api";
import { ReviewCharts } from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { RecommendationList } from "../../../../components/recommendations/RecommendationList";
import { Badge, ErrorState } from "../../../../components/ui";
import { reviewFilters, useFilterStore } from "../../../../lib/stores/filters";
export default function InsightsPage() {
  const f = useFilterStore((s) => s.filters);
  const p = reviewFilters(f);
  const recs = useQuery({
    queryKey: ["recommendations"],
    queryFn: async () =>
      await RecommendationsService.recommendationsApiV1RecommendationsGet(),
  });
  const distribution = useQuery({
    queryKey: ["review-distribution", p],
    queryFn: async () =>
      await ReviewsService.scoreDistributionApiV1ReviewsScoreDistributionGet(p),
  });
  const trends = useQuery({
    queryKey: ["review-trends", p],
    queryFn: async () =>
      await ReviewsService.reviewTrendsApiV1ReviewsTrendsGet(p),
  });
  const failed = [recs, distribution, trends].find((q) => q.error);
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Decision support"
        title="Insights & recommendations"
        description="Deterministic, auditable recommendations paired with governed review-score analytics."
        action={<Badge>No NLP-dependent UI · gate was NO-GO</Badge>}
      />
      <section className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Recommended actions</h2>
        {recs.data && <RecommendationList recommendations={recs.data.data} />}
      </section>
      <section>
        <div className="mb-4">
          <h2 className="text-xl font-semibold">Review analytics</h2>
          <p className="mt-1 text-sm text-muted">
            Score distribution and trends only. Sentiment, keywords, topics, and
            word clouds are intentionally absent.
          </p>
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          {distribution.data && trends.data && (
            <ReviewCharts
              distribution={distribution.data.data}
              trends={trends.data.data}
            />
          )}
        </div>
      </section>
    </>
  );
}
