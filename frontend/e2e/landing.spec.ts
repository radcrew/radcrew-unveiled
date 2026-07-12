import { expect, test } from "../playwright-fixture";

test.describe("landing page", () => {
  test("loads with the nav and logo", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByTestId("nav-logo")).toBeVisible();
    await expect(page.getByTestId("nav-logo")).toHaveText(/radcrew/i);
    // Primary nav actions are present.
    await expect(page.getByTestId("nav-contact")).toBeVisible();
  });

  test("renders the floating chat launcher", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("button", { name: /ask radcrew/i })).toBeVisible();
  });
});
