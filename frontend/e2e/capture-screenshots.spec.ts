import { expect, test, type Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const outDir = path.resolve(__dirname, "../../RECURSOS/screenshots");
const apiHealth =
  process.env.API_HEALTH_URL ?? "https://epintel-api.onrender.com/health";

test.describe.configure({ mode: "serial" });

async function warmApi() {
  for (let attempt = 1; attempt <= 5; attempt += 1) {
    try {
      const response = await fetch(apiHealth, { signal: AbortSignal.timeout(120_000) });
      if (response.ok) return;
    } catch {
      // Render cold start — retry
    }
  }
  throw new Error(`API not ready at ${apiHealth}`);
}

async function waitForLoadingToFinish(page: Page, message: string | RegExp) {
  await expect(page.getByText(message)).toHaveCount(0, { timeout: 120_000 });
}

async function waitForChartSvg(page: Page, minCount = 1) {
  await expect
    .poll(async () => page.locator(".echarts-for-react svg, .colombia-map svg").count(), {
      timeout: 120_000,
      message: "Esperando gráficos SVG renderizados",
    })
    .toBeGreaterThanOrEqual(minCount);
}

async function prepareBrotes(page: Page) {
  const predictionReady = page.waitForResponse(
    (response) =>
      response.url().includes("/api/v1/outbreak-predictions") && response.ok(),
    { timeout: 120_000 },
  );

  await page.goto("/brotes", { waitUntil: "domcontentloaded", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: /ficha territorial/i })).toBeVisible({
    timeout: 60_000,
  });
  await predictionReady;

  await waitForLoadingToFinish(page, /calculando señal territorial/i);
  await waitForLoadingToFinish(page, /cargando serie/i);

  await expect(page.getByText("Casos observados", { exact: true })).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.getByText("¿Qué factores influyen?")).toBeVisible({ timeout: 60_000 });
  await expect(page.locator(".signal-ring span")).toHaveText(/\d/, { timeout: 60_000 });
  await waitForChartSvg(page, 1);
  await page.waitForTimeout(2500);
}

async function prepareMapa(page: Page) {
  const mapReady = page.waitForResponse(
    (response) => response.url().includes("/api/v1/outbreak-map") && response.ok(),
    { timeout: 120_000 },
  );
  const boundariesReady = page.waitForResponse(
    (response) =>
      response.url().includes("/api/v1/territorial-boundaries") && response.ok(),
    { timeout: 120_000 },
  );

  await page.goto("/mapa", { waitUntil: "domcontentloaded", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: /mapa territorial/i })).toBeVisible({
    timeout: 60_000,
  });
  await Promise.all([mapReady, boundariesReady]);

  await waitForLoadingToFinish(page, /cargando mapa territorial/i);
  await expect(page.getByText("Distribución por clasificación")).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.locator(".signal-ring")).toBeVisible({ timeout: 60_000 });
  await expect(page.locator(".colombia-map svg")).toBeVisible({ timeout: 60_000 });
  await page.waitForTimeout(2500);
}

async function prepareLanding(page: Page) {
  await page.goto("/", { waitUntil: "networkidle", timeout: 120_000 });
  await expect(page.getByRole("heading", { name: /anticipa brotes/i })).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.getByRole("link", { name: /abrir radar territorial/i })).toBeVisible({
    timeout: 60_000,
  });
  await page.waitForTimeout(1000);
}

test.describe("capture demo screenshots", () => {
  test.beforeAll(async () => {
    await mkdir(outDir, { recursive: true });
    await warmApi();
  });

  test("capture brotes.png", async ({ page }) => {
    test.setTimeout(180_000);
    await page.setViewportSize({ width: 1440, height: 900 });
    await prepareBrotes(page);
    await page.screenshot({
      path: path.join(outDir, "brotes.png"),
      fullPage: false,
      animations: "disabled",
    });
  });

  test("capture mapa.png", async ({ page }) => {
    test.setTimeout(180_000);
    await page.setViewportSize({ width: 1440, height: 900 });
    await prepareMapa(page);
    await page.screenshot({
      path: path.join(outDir, "mapa.png"),
      fullPage: false,
      animations: "disabled",
    });
  });

  test("capture landing.png", async ({ page }) => {
    test.setTimeout(120_000);
    await page.setViewportSize({ width: 1440, height: 900 });
    await prepareLanding(page);
    await page.screenshot({
      path: path.join(outDir, "landing.png"),
      fullPage: false,
      animations: "disabled",
    });
  });
});
