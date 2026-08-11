"use client";
import { useQuery } from "@tanstack/react-query";
import {
  DashboardService,
  ProductsService,
  SellersService,
} from "../../../../src/generated/api";
import {
  ChartCard,
  DataTable,
  PerformanceBar,
} from "../../../../components/charts/Charts";
import { PageHeader } from "../../../../components/layout/PageHeader";
import { ErrorState } from "../../../../components/ui";
import {
  categoryFilters,
  dateFilters,
  sellerFilters,
  useFilterStore,
} from "../../../../lib/stores/filters";
import { formatCurrency, formatNumber, titleCase } from "../../../../lib/utils";

export default function ProductsPage() {
  const f = useFilterStore((s) => s.filters);
  const categories = useQuery({
    queryKey: ["product-categories", categoryFilters(f)],
    queryFn: async () =>
      await ProductsService.productCategoriesApiV1ProductsCategoriesGet(
        categoryFilters(f),
      ),
  });
  const products = useQuery({
    queryKey: ["product-top", f.dateFrom, f.dateTo, f.category, f.sellerId],
    queryFn: async () =>
      await DashboardService.topProductsApiV1DashboardTopProductsGet({
        ...dateFilters(f),
        category: f.category,
        sellerId: f.sellerId,
        limit: 20,
      }),
  });
  const sellers = useQuery({
    queryKey: ["product-sellers", sellerFilters(f)],
    queryFn: async () =>
      await SellersService.sellerPerformanceApiV1SellersPerformanceGet(
        sellerFilters(f),
      ),
  });
  const failed = [categories, products, sellers].find((q) => q.error);
  if (failed) return <ErrorState error={failed.error} />;
  return (
    <>
      <PageHeader
        eyebrow="Merchandising intelligence"
        title="Products & sellers"
        description="Category, SKU, and seller performance based on delivered revenue, order count, units, and observed review scores."
      />
      <div className="grid gap-4 xl:grid-cols-2">
        {categories.data && (
          <PerformanceBar
            title="Category revenue"
            data={categories.data.data}
          />
        )}
        <ChartCard title="Top products">
          {products.data && (
            <DataTable
              headers={["Product", "Category", "Revenue", "Units", "Orders"]}
              rows={products.data.data.map((r) => [
                r.product_id.slice(0, 12),
                titleCase(r.category ?? "uncategorized"),
                formatCurrency(r.revenue),
                r.units,
                r.order_count,
              ])}
            />
          )}
        </ChartCard>
        <ChartCard className="xl:col-span-2" title="Seller performance">
          {sellers.data && (
            <DataTable
              headers={["Seller", "Revenue", "Orders", "Units", "Avg review"]}
              rows={sellers.data.data.map((r) => [
                r.key.slice(0, 12),
                formatCurrency(r.revenue),
                formatNumber(r.order_count),
                formatNumber(r.units ?? 0),
                r.average_review_score
                  ? Number(r.average_review_score).toFixed(2)
                  : "—",
              ])}
            />
          )}
        </ChartCard>
      </div>
    </>
  );
}
