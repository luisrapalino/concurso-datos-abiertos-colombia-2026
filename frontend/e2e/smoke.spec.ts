import { expect, test } from "@playwright/test";

test.describe("Institutional MVP smoke", () => {
  test("home dashboard loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /panel territorial/i })).toBeVisible();
  });

  test("risk page loads for demo filters", async ({ page }) => {
    await page.goto("/riesgo");
    await expect(page.getByRole("heading", { name: /riesgo territorial/i })).toBeVisible();
  });

  test("map page loads", async ({ page }) => {
    await page.goto("/mapa");
    await expect(page.getByText(/municipios con score de riesgo/i)).toBeVisible({
      timeout: 20_000,
    });
  });

  test("insights page loads", async ({ page }) => {
    await page.goto("/insights");
    await expect(page.getByRole("heading", { name: /insights/i })).toBeVisible();
  });
});
