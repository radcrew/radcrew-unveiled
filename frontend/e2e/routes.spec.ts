import { expect, test } from "../playwright-fixture";

test.describe("journal routes", () => {
  test("opens a post from the index", async ({ page }) => {
    await page.goto("/journal");

    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Journal");

    // Each card is one big link, so its accessible name is the whole card.
    // Match on href instead, which does not change when the copy does.
    await page.locator('a[href^="/journal/"]').first().click();

    await expect(page).toHaveURL(/\/journal\/[a-z-]+$/);
    await expect(page.getByRole("heading", { level: 1 })).not.toHaveText("Journal");
  });

  test("renders 404 for an unknown post slug", async ({ page }) => {
    await page.goto("/journal/not-a-real-post");

    await expect(page.getByText("404")).toBeVisible();
  });
});
