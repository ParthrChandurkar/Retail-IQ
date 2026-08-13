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
      "customer-analytics.png",
      "/dashboard/customers",
      "Segments, RFM & value",
      "Profiled customers",
    ],
    [
      "classification-dashboard.png",
      "/dashboard/classification",
      "Satisfaction classification",
      "Single-record prediction",
    ],
    [
      "insights-dashboard.png",
      "/dashboard/insights",
      "Insights & recommendations",
      "Review score distribution",
    ],
  ] as const) {
    await page.goto(`${baseURL}${route}`);
    await page.getByText(heading, { exact: true }).waitFor({ timeout: 30_000 });
    await page
      .getByText(readyText, { exact: true })
      .waitFor({ timeout: 30_000 });
    await page.waitForTimeout(750);
    await page.screenshot({ path: path.join(output, name), fullPage: true });
  }
  await browser.close();
}

void main();
