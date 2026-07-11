import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const outDir = path.resolve(__dirname, "../../RECURSOS/screenshots");
const apiHealth =
  process.env.API_HEALTH_URL ?? "https://epintel-api.onrender.com/health";

const captures = [
  {
    file: "brotes.png",
    path: "/brotes",
    heading: /ficha territorial/i,
  },
  {
    file: "mapa.png",
    path: "/mapa",
    heading: /mapa territorial/i,
  },
  {
    file: "landing.png",
    path: "/",
    heading: /anticipa brotes/i,
  },
] as const;

test.describe.configure({ mode: "serial" });

test.describe("capture demo screenshots", () => {
  test.beforeAll(async () => {
    await mkdir(outDir, { recursive: true });
    for (let attempt = 1; attempt <= 3; attempt += 1) {
      try {
        const response = await fetch(apiHealth, { signal: AbortSignal.timeout(90_000) });
        if (response.ok) return;
      } catch {
        // retry warm-up
      }
    }
  });

  for (const spec of captures) {
    test(`capture ${spec.file}`, async ({ page }) => {
      test.setTimeout(120_000);
      await page.setViewportSize({ width: 1440, height: 900 });

      const apiResponse = page
        .waitForResponse(
          (response) => response.url().includes("/api/v1/") && response.ok(),
          { timeout: 90_000 },
        )
        .catch(() => null);

      await page.goto(spec.path, { waitUntil: "domcontentloaded", timeout: 90_000 });
      await expect(page.getByRole("heading", { name: spec.heading })).toBeVisible({
        timeout: 60_000,
      });
      if (spec.path !== "/") {
        await apiResponse;
      }
      await page.waitForTimeout(1500);

      await page.screenshot({
        path: path.join(outDir, spec.file),
        fullPage: false,
        animations: "disabled",
      });
    });
  }
});
