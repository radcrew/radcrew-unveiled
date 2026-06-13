import { expect, test } from "../playwright-fixture";

test.describe("landing page", () => {
  test("loads with the nav and logo", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByTestId("nav-logo")).toBeVisible();
    await expect(page.getByTestId("nav-logo")).toHaveText(/radcrew/i);
    // Primary nav actions are present.
    await expect(page.getByTestId("nav-team")).toBeVisible();
    await expect(page.getByTestId("nav-contact")).toBeVisible();
  });

  test("nav 'Team' scrolls the team section into view", async ({ page }) => {
    await page.goto("/");

    const team = page.locator("#team");
    await page.getByTestId("nav-team").click();

    await expect(team).toBeInViewport({ timeout: 10_000 });
  });

  test("renders the floating chat launcher", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("button", { name: /ask radcrew/i })).toBeVisible();
  });
});
