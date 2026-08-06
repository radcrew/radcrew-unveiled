import { expect, test } from "../playwright-fixture";

test.describe("work routes", () => {
  test("lists every case study and links each to its own page", async ({ page }) => {
    await page.goto("/work");

    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Selected Work");
    await expect(page.getByRole("link", { name: /read the case study/i })).toHaveCount(3);
  });

  test("opens a case study from the landing page carousel", async ({ page }) => {
    await page.goto("/");

    await page
      .getByRole("link", { name: /read the case study/i })
      .first()
      .click();

    await expect(page).toHaveURL(/\/work\/real-estate-consultant$/);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Real Estate Consultant");
    // The narrative sections are what distinguish the detail page from the card.
    await expect(page.getByRole("heading", { name: "The challenge" })).toBeVisible();
  });

  test("renders 404 for an unknown project slug", async ({ page }) => {
    await page.goto("/work/not-a-real-project");

    await expect(page.getByText("404")).toBeVisible();
  });
});

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
