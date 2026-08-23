import { expect, test, type Page, type Route } from "@playwright/test";
import path from "node:path";

const generatedAt = "2026-08-22T12:00:00Z";
const envelope = (data: unknown) => ({ data, generated_at: generatedAt });
const testUser = {
  user_id: 1,
  email: "qa@example.com",
  full_name: "Migration QA",
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

const performance = {
  key: "Electronics / Phones",
  revenue: "250844101.42",
  total_profit: "37553051.14",
  order_count: 1000,
  units: 1200,
  avg_discount_pct: "25.13",
  profit_margin_pct: "14.97",
};
const region = {
  state: "Maharashtra",
  region: "West",
  city_type: "Tier 1",
  revenue: "250844101.42",
  total_profit: "37553051.14",
  order_count: 1000,
  customer_count: 1000,
  avg_discount_pct: "25.13",
  profit_margin_pct: "14.97",
  latitude: 19.7515,
  longitude: 75.7139,
};

async function mockApi(page: Page) {
  await page.route("**/api/v1/**", async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    if (
      pathname === "/api/v1/auth/refresh" ||
      pathname === "/api/v1/auth/login"
    )
      return json(
        route,
        envelope({
          access_token: "m8-token",
          token_type: "bearer",
          expires_in: 900,
          user: testUser,
        }),
      );
    if (pathname === "/api/v1/auth/me") return json(route, envelope(testUser));
    if (pathname === "/api/v1/dashboard/summary")
      return json(
        route,
        envelope({
          period_start: "2019-01-01",
          period_end: "2023-12-31",
          total_revenue: "250844101.42",
          total_profit: "37553051.14",
          total_orders: 100000,
          total_customers: 100000,
          average_order_value: "2508.44",
          avg_discount_pct: "25.13",
          profit_margin_pct: "14.97",
          revenue_mom_growth_pct: "1.23",
          revenue_yoy_growth_pct: "4.56",
        }),
      );
    if (pathname === "/api/v1/dashboard/revenue-trend")
      return json(
        route,
        envelope([
          {
            date: "2023-01-01",
            revenue: "1000",
            total_profit: "150",
            order_count: 8,
            customer_count: 8,
          },
        ]),
      );
    if (
      pathname === "/api/v1/dashboard/top-categories" ||
      pathname === "/api/v1/products/categories" ||
      pathname === "/api/v1/products/performance"
    )
      return json(route, envelope([performance]));
    if (pathname === "/api/v1/products/discount-profit")
      return json(
        route,
        envelope([
          {
            category: "Electronics",
            sub_category: "Phones",
            discount_band: "high",
            order_count: 100,
            revenue: "100000",
            total_profit: "9000",
            avg_discount_pct: "42",
            avg_profit_margin_pct: "9",
          },
        ]),
      );
    if (pathname === "/api/v1/customers/segments")
      return json(
        route,
        envelope([
          {
            segment: "Corporate",
            order_value_tier: "q4",
            city_type: "Tier 1",
            customer_count: 10,
            avg_order_value: "40000",
            avg_profit: "6000",
            avg_discount_pct: "20",
          },
        ]),
      );
    if (pathname === "/api/v1/customers/profiles")
      return json(route, {
        ...envelope([
          {
            customer_id: "CUST000001",
            order_date: "2023-01-01",
            recency_days: 1,
            order_value: "40000",
            profit: "6000",
            discount_pct: "20",
            segment: "Corporate",
            city_type: "Tier 1",
            region: "West",
            state: "Maharashtra",
            order_value_tier: "q4",
          },
        ]),
        page: 1,
        page_size: 40,
        total: 100000,
      });
    if (pathname === "/api/v1/customers/order-value-distribution")
      return json(route, envelope([{ bucket: "q4", count: 25000 }]));
    if (
      pathname === "/api/v1/regions/sales" ||
      pathname === "/api/v1/regions/choropleth"
    )
      return json(route, envelope([region]));
    if (pathname === "/api/v1/regions/shipping-performance")
      return json(
        route,
        envelope([
          {
            date: "2023-01-01",
            ship_mode: "Standard Class",
            region: "West",
            order_count: 10,
            avg_shipping_days: "3.2",
            median_shipping_days: "3",
            min_shipping_days: 1,
            max_shipping_days: 7,
          },
        ]),
      );
    if (pathname === "/api/v1/analytics/seasonality")
      return json(
        route,
        envelope([
          {
            month_number: 1,
            average_daily_revenue: "100",
            total_revenue: "3100",
            order_count: 10,
          },
        ]),
      );
    if (pathname === "/api/v1/analytics/correlation-matrix")
      return json(
        route,
        envelope({
          fields: ["sales", "profit"],
          correlation: {
            sales: { sales: 1, profit: 0.58 },
            profit: { sales: 0.58, profit: 1 },
          },
          observations: 100000,
        }),
      );
    if (pathname === "/api/v1/analytics/hypothesis-tests")
      return json(
        route,
        envelope([
          {
            name: "Chi-Square: category × customer segment",
            statistic: 4.2,
            p_value: 0.52,
            effect_size_name: "Cramer's V",
            effect_size: 0.004,
            conclusion: "No meaningful association was found.",
          },
          {
            name: "One-way ANOVA: profit margin across city types",
            statistic: 0.637,
            p_value: 0.5289,
            effect_size_name: "Eta-squared",
            effect_size: 0.00001,
            conclusion:
              "Profit margins do not differ significantly across city types.",
          },
          {
            name: "Welch t-test: profit margin for high- vs low-discount orders",
            statistic: -150.2,
            p_value: 0,
            effect_size_name: "Cohen's d",
            effect_size: -1.2,
            conclusion: "High discounts materially reduce profit margin.",
          },
        ]),
      );
    if (pathname === "/api/v1/analytics/descriptive-stats")
      return json(
        route,
        envelope([
          {
            field: "sales",
            mean: 100,
            median: 90,
            mode: 80,
            std: 10,
            variance: 100,
            q1: 70,
            q3: 120,
          },
        ]),
      );
    if (pathname === "/api/v1/analytics/broad-screen")
      return json(
        route,
        envelope({
          field_summary: [
            {
              categorical_field: "city_type",
              groups: 3,
              max_effect_size: 0.00001,
              any_fdr_significant: false,
              classification: "valid_dimension_no_material_numeric_effect",
            },
          ],
        }),
      );
    if (pathname === "/api/v1/classification/model-info")
      return json(
        route,
        envelope({
          model_id: 4,
          target_variable: "is_high_profit_order",
          algorithm: "Gradient Boosting",
          trained_at: generatedAt,
          positive_class: "high_profit_order",
          negative_class: "standard_profit_order",
          prediction_probability_semantics: "confidence in predicted label",
          feature_columns: [],
          top_global_features: [],
        }),
      );
    if (pathname === "/api/v1/classification/metrics")
      return json(
        route,
        envelope({
          model_id: 4,
          algorithm: "Gradient Boosting",
          positive_class: "high_profit_order",
          negative_class: "standard_profit_order",
          accuracy: 0.84875,
          precision_high_profit_order: 0.682769,
          recall_high_profit_order: 0.7378,
          f1_high_profit_order: 0.709218,
          roc_auc: 0.923453,
          cv_f1_scores: [0.71],
          cv_mean_f1_high_profit_order: 0.712965,
          cv_roc_auc_scores: [0.92],
          cv_mean_roc_auc: 0.92424,
          confusion_matrix: {
            column_headers: ["high_profit_order", "standard_profit_order"],
            rows: [
              {
                actual_label: "high_profit_order",
                high_profit_order: 3689,
                standard_profit_order: 1311,
              },
              {
                actual_label: "standard_profit_order",
                high_profit_order: 1714,
                standard_profit_order: 13286,
              },
            ],
          },
        }),
      );
    if (pathname === "/api/v1/classification/feature-importance")
      return json(
        route,
        envelope([{ feature: "sales", importance: 0.808818 }]),
      );
    if (pathname === "/api/v1/classification/predict")
      return json(
        route,
        envelope({
          model_id: 4,
          target_variable: "is_high_profit_order",
          predicted_label: "high_profit_order",
          predicted_probability: 0.8327976187991819,
          top_global_features: [{ feature: "sales", importance: 0.808818 }],
        }),
      );
    if (pathname === "/api/v1/recommendations")
      return json(
        route,
        envelope([
          {
            id: "margin-high",
            category: "profitability",
            severity: "high",
            title: "Protect margin",
            description: "Examine high-discount pricing controls.",
            supporting_metric: { profit_margin_pct: 9 },
          },
        ]),
      );
    return json(route, envelope([]));
  });
}

async function login(page: Page) {
  await page.goto("/login?next=/dashboard");
  await page
    .getByLabel("Email")
    .fill(process.env.E2E_ADMIN_EMAIL ?? "qa@example.com");
  await page
    .getByLabel("Password")
    .fill(process.env.E2E_ADMIN_PASSWORD ?? "m8-password");
  await page.getByRole("button", { name: "Sign in securely" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText("Business performance")).toBeVisible({
    timeout: 45_000,
  });
}

async function navigate(page: Page, name: string) {
  const menu = page.getByRole("button", { name: "Open navigation" });
  const mobile = await menu.isVisible();
  if (mobile) await menu.click();
  await page.getByRole("link", { name }).click();
  if (mobile) await expect(menu).toBeFocused();
}

test.beforeEach(async ({ page }) => {
  if (process.env.LIVE_E2E !== "1") await mockApi(page);
});

test("login, Indian currency, filter routing, restored focus, and navigation", async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  page.on(
    "console",
    (message) =>
      message.type() === "error" && consoleErrors.push(message.text()),
  );
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  await login(page);
  await expect(
    page.getByText(
      process.env.LIVE_E2E === "1"
        ? "₹2,50,84,41,014.18"
        : "₹25,08,44,101.42",
    ),
  ).toBeVisible();

  const routedRevenue = page.waitForRequest((request) => {
    const url = new URL(request.url());
    return (
      url.pathname === "/api/v1/dashboard/revenue-trend" &&
      url.searchParams.get("category") === "Electronics"
    );
  });
  await page.getByLabel("Category", { exact: true }).fill("Electronics");
  await expect(page).toHaveURL(/category=Electronics/);
  await routedRevenue;

  await navigate(page, "Customers");
  await expect(
    page.getByText("Cross-sectional customer profiles"),
  ).toBeVisible();
  await page.keyboard.press("Tab");
  const focus = await page.evaluate(() => ({
    tag: document.activeElement?.tagName,
    outline: document.activeElement
      ? getComputedStyle(document.activeElement).outlineStyle
      : "none",
  }));
  expect(focus.tag).not.toBe("BODY");
  expect(focus.outline).not.toBe("none");
  expect(consoleErrors).toEqual([]);
});

test("classification uses the exact M6 inputs and outcome confidence", async ({
  page,
}) => {
  await login(page);
  await navigate(page, "Classification");
  await expect(
    page.getByText("High-profit order classification"),
  ).toBeVisible();
  const expectedFields = [
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
  ];
  for (const field of expectedFields)
    await expect(page.locator(`#predict-${field}`)).toBeVisible();
  await page.getByRole("button", { name: "Predict profit outcome" }).click();
  await expect(
    page.getByText("83% confident: high_profit_order"),
  ).toBeVisible();
  await expect(
    page.getByText(/Confidence is for the displayed outcome/),
  ).toBeVisible();
});

test("analytics distinguishes null and significant findings", async ({
  page,
}) => {
  await login(page);
  await navigate(page, "Analytics");
  await expect(
    page.getByRole("heading", {
      name: "One-way ANOVA: profit margin across city types",
    }),
  ).toBeVisible();
  await expect(page.getByText("0.5289 · Not significant")).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "Welch t-test: profit margin for high- vs low-discount orders",
    }),
  ).toBeVisible();
  await expect(page.getByText("< 0.0001 · Significant")).toBeVisible();
});

test("every migrated dashboard route renders its live API-backed view", async ({
  page,
}) => {
  await login(page);
  const routes = [
    ["/dashboard/products", "Category & sub-category performance"],
    ["/dashboard/regional", "Trusted geography & shipping"],
    ["/dashboard/insights", "Insights & recommendations"],
    ["/settings", "Account & platform"],
  ] as const;
  for (const [path, heading] of routes) {
    await page.goto(path);
    await expect(page.getByRole("heading", { name: heading })).toBeVisible({
      timeout: 30_000,
    });
  }
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
  await login(page);
  await navigate(page, "Sales");
  await expect(page.getByText("Revenue, profit & demand")).toBeVisible();
  const started = Date.now();
  await navigate(page, "Overview");
  await expect(page.getByText("Business performance")).toBeVisible();
  const kpiFirstPaintMs = Date.now() - started;
  console.log(`KPI_FIRST_PAINT_MS=${kpiFirstPaintMs}`);
  expect(kpiFirstPaintMs).toBeLessThan(1_500);
});
