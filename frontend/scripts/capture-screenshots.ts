import { chromium } from "@playwright/test";
import path from "node:path";

async function main() {
  const baseURL = process.env.SCREENSHOT_BASE_URL ?? "http://localhost:3000";
  const email = process.env.SCREENSHOT_ADMIN_EMAIL;
  const password = process.env.SCREENSHOT_ADMIN_PASSWORD;
  const requestedName = process.env.SCREENSHOT_NAME;
  if (!email || !password) {
    throw new Error(
      "SCREENSHOT_ADMIN_EMAIL and SCREENSHOT_ADMIN_PASSWORD are required",
    );
  }

  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
    args: ["--disable-gpu", "--renderer-process-limit=2"],
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  await page.goto(`${baseURL}/login?next=/dashboard`);
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in securely" }).click();
  await page.getByText("Business performance").waitFor({ timeout: 30_000 });

  const output = path.resolve(process.cwd(), "..", "docs", "screenshots");
  for (const [name, route, heading, apiPaths] of [
    [
      "executive-dashboard.png",
      "/dashboard",
      "Business performance",
      ["/api/v1/dashboard/summary"],
    ],
    [
      "sales-dashboard.png",
      "/dashboard/sales",
      "Revenue, profit & demand",
      ["/api/v1/dashboard/revenue-trend"],
    ],
    [
      "customer-analytics.png",
      "/dashboard/customers",
      "Cross-sectional customer profiles",
      ["/api/v1/customers/segments"],
    ],
    [
      "product-dashboard.png",
      "/dashboard/products",
      "Category & sub-category performance",
      ["/api/v1/products/performance"],
    ],
    [
      "regional-dashboard.png",
      "/dashboard/regional",
      "Trusted geography & shipping",
      ["/api/v1/regions/choropleth"],
    ],
    [
      "classification-dashboard.png",
      "/dashboard/classification",
      "High-profit order classification",
      [
        "/api/v1/classification/model-info",
        "/api/v1/classification/metrics",
        "/api/v1/classification/feature-importance",
      ],
    ],
    [
      "analytics-dashboard.png",
      "/dashboard/analytics",
      "Evidence behind the decisions",
      [
        "/api/v1/analytics/correlation-matrix",
        "/api/v1/analytics/hypothesis-tests",
        "/api/v1/analytics/descriptive-stats",
        "/api/v1/analytics/broad-screen",
      ],
    ],
    [
      "insights-dashboard.png",
      "/dashboard/insights",
      "Insights & recommendations",
      ["/api/v1/recommendations"],
    ],
  ] as const) {
    if (requestedName && requestedName !== name) continue;
    const liveData = Promise.all(
      apiPaths.map((apiPath) =>
        page.waitForResponse(
          (response) => response.url().includes(apiPath) && response.ok(),
          { timeout: 120_000 },
        ),
      ),
    );
    await page.goto(`${baseURL}${route}`);
    await page
      .getByRole("heading", { name: heading, exact: true })
      .waitFor({ timeout: 30_000 });
    await liveData;
    await page.waitForTimeout(1_000);
    await page.screenshot({
      path: path.join(output, name),
      fullPage: name !== "regional-dashboard.png",
      animations: "disabled",
      timeout: 120_000,
    });
  }
  await browser.close();
}

void main();
