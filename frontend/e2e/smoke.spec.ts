import { expect, test } from "@playwright/test";

test.describe("Radar de brotes — smoke", () => {
  test("landing page loads with hero and CTA", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: /anticipa brotes con datos abiertos/i }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: /abrir radar territorial/i })).toBeVisible();
  });

  test("radar page loads with priority table", async ({ page }) => {
    await page.goto("/radar");
    await expect(page.getByRole("heading", { name: /¿dónde revisar primero\?/i })).toBeVisible();
    await expect(page.getByText(/prioridad territorial/i)).toBeVisible();
  });

  test("territorial ficha loads", async ({ page }) => {
    await page.goto("/brotes");
    await expect(page.getByRole("heading", { name: /ficha territorial/i })).toBeVisible();
  });

  test("map page loads outbreak layer", async ({ page }) => {
    await page.goto("/mapa");
    await expect(page.getByRole("heading", { name: /mapa de señales/i })).toBeVisible();
    await expect(page.getByText(/ciudades principales/i)).toBeVisible({
      timeout: 20_000,
    });
  });

  test("report page loads", async ({ page }) => {
    await page.goto("/informe");
    await expect(page.getByRole("heading", { name: /informe para vigilancia/i })).toBeVisible();
  });

  test("datasets page loads", async ({ page }) => {
    await page.goto("/datos");
    await expect(page.getByRole("heading", { name: /fuentes de datos/i })).toBeVisible();
    await expect(page.getByText(/portal datos\.gov\.co/i).first()).toBeVisible({
      timeout: 20_000,
    });
  });

  test("deprecated routes redirect to radar", async ({ page }) => {
    await page.goto("/riesgo");
    await expect(page).toHaveURL("/radar");
  });
});
