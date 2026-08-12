import { expect, test, type Page, type Route } from "@playwright/test";
import path from "node:path";

const generatedAt = "2026-08-12T12:00:00Z";
const envelope = (data: unknown) => ({ data, generated_at: generatedAt });
const testUser = {
  user_id: 1,
  email: "qa@retailiq.local",
  full_name: "Phase 8 QA",
  role: "admin",
  is_active: true,
};

async function json(route: Route, body: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function mockApi(page: Page) {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    if (pathname === "/api/v1/auth/refresh")
      return json(
        route,
        envelope({
          access_token: "phase8-refresh-token",
          token_type: "bearer",
          expires_in: 900,
          user: testUser,
        }),
      );
    if (pathname === "/api/v1/auth/login")
      return json(
        route,
        envelope({
          access_token: "phase8-token",
          token_type: "bearer",
          expires_in: 900,
          user: testUser,
        }),
      );
    if (pathname === "/api/v1/dashboard/summary")
      return json(
        route,
        envelope({
          period_start: "2016-09-01",
          period_end: "2018-08-31",
          total_revenue: "13259143.27",
          total_orders: 96478,
          total_customers: 93358,
          average_order_value: "137.43",
          revenue_mom_growth_pct: "1.23",
          revenue_yoy_growth_pct: "4.56",
        }),
      );
    if (pathname === "/api/v1/dashboard/revenue-trend")
      return json(
        route,
        envelope([
          {
            date: "2018-01-01",
            revenue: "1000",
            order_count: 8,
            customer_count: 8,
          },
        ]),
      );
    if (
      pathname.includes("/dashboard/top-categories") ||
      pathname.includes("/dashboard/top-sellers")
    )
      return json(
        route,
        envelope([
          {
            key: "health_beauty",
            revenue: "1000",
            order_count: 8,
            units: 9,
            average_review_score: "4.1",
          },
        ]),
      );
    if (pathname === "/api/v1/dashboard/top-products")
      return json(
        route,
        envelope([
          {
            product_id: "product-001",
            category: "health_beauty",
            revenue: "500",
            units: 4,
            order_count: 4,
          },
        ]),
      );
    if (pathname === "/api/v1/customers/segments")
      return json(
        route,
        envelope([
          {
            segment: "champions",
            customer_count: 10,
            avg_clv: "400",
            avg_order_count: "2",
          },
        ]),
      );
    if (pathname === "/api/v1/customers/rfm")
      return json(route, {
        ...envelope([
          {
            customer_unique_id: "customer-001",
            first_order_ts: null,
            last_order_ts: null,
            order_count: 2,
            total_spend: "400",
            primary_state: "SP",
            primary_city: "Sao Paulo",
            recency_score: 5,
            frequency_score: 5,
            monetary_score: 5,
            rfm_segment: "champions",
            clv_historical: "400",
          },
        ]),
        page: 1,
        page_size: 40,
        total: 1,
      });
    if (pathname === "/api/v1/customers/clv-distribution")
      return json(route, envelope([{ bucket: "10", count: 10 }]));
    if (pathname === "/api/v1/customers/repeat-purchase-rate")
      return json(
        route,
        envelope({
          total_customers: 100,
          repeat_customers: 3,
          repeat_purchase_rate_pct: "3.00",
        }),
      );
    if (pathname === "/api/v1/classification/model-info")
      return json(
        route,
        envelope({
          model_id: 1,
          target_variable: "low_satisfaction",
          algorithm: "XGBoost",
          trained_at: generatedAt,
          positive_class: "low_satisfaction",
          negative_class: "high_satisfaction",
          prediction_probability_semantics: "confidence in predicted label",
          feature_columns: [],
          top_global_features: [],
        }),
      );
    if (pathname === "/api/v1/classification/metrics")
      return json(
        route,
        envelope({
          model_id: 1,
          algorithm: "XGBoost",
          positive_class: "low_satisfaction",
          negative_class: "high_satisfaction",
          accuracy: 0.8,
          precision_low_satisfaction: 0.7,
          recall_low_satisfaction: 0.6,
          f1_low_satisfaction: 0.65,
          roc_auc: 0.76,
          cv_f1_scores: [0.64],
          cv_mean_f1_low_satisfaction: 0.64,
          cv_roc_auc_scores: [0.75],
          cv_mean_roc_auc: 0.75,
          confusion_matrix: {
            column_headers: ["low_satisfaction", "high_satisfaction"],
            rows: [
              {
                actual_label: "low_satisfaction",
                low_satisfaction: 10,
                high_satisfaction: 2,
              },
              {
                actual_label: "high_satisfaction",
                low_satisfaction: 3,
                high_satisfaction: 20,
              },
            ],
          },
        }),
      );
    if (pathname === "/api/v1/classification/feature-importance")
      return json(
        route,
        envelope([{ feature: "delivery_delay_hours", importance: 0.4 }]),
      );
    if (pathname === "/api/v1/classification/predict")
      return json(
        route,
        envelope({
          model_id: 1,
          target_variable: "low_satisfaction",
          predicted_label: "low_satisfaction",
          predicted_probability: 0.89,
          top_global_features: [
            { feature: "delivery_delay_hours", importance: 0.4 },
          ],
        }),
      );
    return json(route, envelope([]));
  });
}

async function login(page: Page) {
  await page.goto("/login?next=/dashboard");
  await page
    .getByLabel("Email")
    .fill(process.env.E2E_ADMIN_EMAIL ?? "qa@retailiq.local");
  await page
    .getByLabel("Password")
    .fill(process.env.E2E_ADMIN_PASSWORD ?? "phase8-password");
  await page.getByRole("button", { name: "Sign in securely" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Business performance")).toBeVisible({
    timeout: 20_000,
  });
}

test.beforeEach(async ({ page }) => {
  if (process.env.LIVE_E2E !== "1") await mockApi(page);
});

test("login, dashboard, filter routing, keyboard focus, and navigation", async ({
  page,
}) => {
  test.setTimeout(60_000);
  const consoleErrors: string[] = [];
  page.on(
    "console",
    (message) =>
      message.type() === "error" && consoleErrors.push(message.text()),
  );
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  await login(page);

  const category = page.getByLabel("Category");
  const routedRevenue = page.waitForRequest((request) => {
    const url = new URL(request.url());
    return (
      url.pathname === "/api/v1/dashboard/revenue-trend" &&
      url.searchParams.get("category") === "health_beauty"
    );
  });
  await category.fill("health_beauty");
  await expect(page).toHaveURL(/category=health_beauty/);
  await routedRevenue;

  if (await page.getByRole("button", { name: "Open navigation" }).isVisible())
    await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Customers" }).click();
  await expect(page.getByText("Segments, RFM & value")).toBeVisible();

  await page.keyboard.press("Tab");
  const focusStyle = await page.evaluate(() => {
    const element = document.activeElement;
    return element ? getComputedStyle(element).outlineStyle : "none";
  });
  expect(focusStyle).not.toBe("none");
  expect(consoleErrors).toEqual([]);
});

test("classification prediction reports confidence in the returned outcome", async ({
  page,
}) => {
  test.setTimeout(60_000);
  await login(page);
  if (await page.getByRole("button", { name: "Open navigation" }).isVisible())
    await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Classification" }).click();
  await expect(page.getByText("Satisfaction classification")).toBeVisible();

  const values: Record<string, string> = {
    entity_id: "order-phase8",
    total_price: "100",
    total_freight: "10",
    item_count: "1",
    product_count: "1",
    seller_count: "1",
    average_item_price: "100",
    maximum_item_price: "100",
    customer_state: "SP",
    seller_state: "SP",
    dominant_category: "health_beauty",
    primary_payment_type: "credit_card",
    purchase_month: "8",
    purchase_weekday: "3",
    purchase_hour: "14",
  };
  for (const [field, value] of Object.entries(values))
    await page.locator(`#predict-${field}`).fill(value);
  await page
    .getByRole("button", { name: "Predict satisfaction outcome" })
    .click();
  await expect(
    page.getByText(/\d+% confident: (low|high) satisfaction/),
  ).toBeVisible({ timeout: 20_000 });
  await expect(
    page.getByText(/not a fixed probability of low satisfaction/i),
  ).toBeVisible();
});

test("dashboard has no serious automated accessibility violations", async ({
  page,
}) => {
  await login(page);
  await page.addScriptTag({
    path: path.join(process.cwd(), "node_modules", "axe-core", "axe.min.js"),
  });
  const violations = await page.evaluate(async () => {
    const axe = (
      window as unknown as {
        axe: {
          run: () => Promise<{
            violations: Array<{ impact: string | null; id: string }>;
          }>;
        };
      }
    ).axe;
    const result = await axe.run();
    return result.violations.filter(
      (item) => item.impact === "critical" || item.impact === "serious",
    );
  });
  expect(violations).toEqual([]);
});

test("warm dashboard KPI first paint meets the 1.5 second NFR", async ({
  page,
}) => {
  test.setTimeout(60_000);
  await login(page);
  if (await page.getByRole("button", { name: "Open navigation" }).isVisible())
    await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Sales" }).click();
  await expect(page.getByText("Revenue & demand")).toBeVisible();
  if (await page.getByRole("button", { name: "Open navigation" }).isVisible())
    await page.getByRole("button", { name: "Open navigation" }).click();
  const started = Date.now();
  await page.getByRole("link", { name: "Overview" }).click();
  await expect(page.getByText("Business performance")).toBeVisible();
  const kpiFirstPaintMs = Date.now() - started;
  console.log(`KPI_FIRST_PAINT_MS=${kpiFirstPaintMs}`);
  expect(kpiFirstPaintMs).toBeLessThan(1_500);
});
