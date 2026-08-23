"use client";

import { useQuery } from "@tanstack/react-query";
import { ProductsService } from "../../../../src/generated/api";
import {
  ChartCard,
  DataTable,
  DiscountProfitChart,
  PerformanceBar,
} from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import {
  categoryFilters,
  discountFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import {
  formatCurrency,
  formatNumber,
  formatPercent,
  titleCase,
} from "../../../../lib/utils";

export default function ProductsPage() {
  const filters = useFilterStore((state) => state.filters);
  const categories = useQuery({
    queryKey: ["product-categories", categoryFilters(filters)],
    queryFn: () =>
      ProductsService.productCategoriesApiV1ProductsCategoriesGet(
        categoryFilters(filters),
      ),
  });
  const subCategories = useQuery({
    queryKey: ["product-sub-categories", categoryFilters(filters)],
    queryFn: () =>
      ProductsService.productPerformanceApiV1ProductsPerformanceGet(
        categoryFilters(filters),
      ),
  });
  const discountProfit = useQuery({
    queryKey: ["discount-profit", discountFilters(filters)],
    queryFn: () =>
      ProductsService.discountProfitApiV1ProductsDiscountProfitGet(
        discountFilters(filters),
      ),
  });
  const failed = [categories, subCategories, discountProfit].find(
    (query) => query.error,
  );
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Merchandising intelligence"
        title="Category & sub-category performance"
        description="Product IDs do not repeat, so every product view stays at the meaningful category and sub-category grains."
      />
      <div className="grid gap-4 xl:grid-cols-2">
        {categories.data && (
          <PerformanceBar
            title="Category revenue"
            data={categories.data.data}
          />
        )}
        {discountProfit.data && (
          <DiscountProfitChart data={discountProfit.data.data} />
        )}
        <ChartCard className="xl:col-span-2" title="Sub-category profitability">
          {subCategories.data && (
            <DataTable
              headers={[
                "Category / sub-category",
                "Revenue",
                "Profit",
                "Margin",
                "Average discount",
                "Orders",
              ]}
              rows={subCategories.data.data.map((row) => [
                titleCase(row.key),
                formatCurrency(row.revenue),
                formatCurrency(row.total_profit),
                formatPercent(row.profit_margin_pct, 2),
                formatPercent(row.avg_discount_pct, 2),
                formatNumber(row.order_count),
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
