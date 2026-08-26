import { chromium } from "@playwright/test";
import path from "node:path";

async function main() {
  const baseURL = process.env.SCREENSHOT_BASE_URL ?? "http://localhost:3000";
  const email = process.env.SCREENSHOT_ADMIN_EMAIL;
  const password = process.env.SCREENSHOT_ADMIN_PASSWORD;
  if (!email || !password) {
    throw new Error(
      "SCREENSHOT_ADMIN_EMAIL and SCREENSHOT_ADMIN_PASSWORD are required",
    );
  }

  const browser = await chromium.launch({
    executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
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
  for (const [name, route, heading, readyText] of [
    [
      "executive-dashboard.png",
      "/dashboard",
      "Business performance",
      "Top products",
    ],
    [
      "sales-dashboard.png",
      "/dashboard/sales",
      "Revenue, profit & demand",
      "Category performance",
    ],
    [
      "customer-analytics.png",
      "/dashboard/customers",
      "Cross-sectional customer profiles",
      "Order-value distribution",
    ],
    [
      "product-dashboard.png",
      "/dashboard/products",
      "Category & sub-category performance",
      "Sub-category profitability",
    ],
    [
      "regional-dashboard.png",
      "/dashboard/regional",
      "Trusted geography & shipping",
      "Indian state choropleth",
    ],
    [
      "classification-dashboard.png",
      "/dashboard/classification",
      "High-profit order classification",
      "Global feature importance",
    ],
    [
      "analytics-dashboard.png",
      "/dashboard/analytics",
      "Evidence behind the decisions",
      "Broad categorical-vs-numeric screen",
    ],
    [
      "insights-dashboard.png",
      "/dashboard/insights",
      "Insights & recommendations",
      "Discount-margin evidence",
    ],
  ] as const) {
    await page.goto(`${baseURL}${route}`);
    await page
      .getByRole("heading", { name: heading, exact: true })
      .waitFor({ timeout: 30_000 });
    await page
      .getByText(readyText, { exact: true })
      .waitFor({ timeout: 30_000 });
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1_000);
    await page.screenshot({ path: path.join(output, name), fullPage: true });
  }
  await browser.close();
}

void main();
