import { expect, test } from "../playwright-fixture";

/**
 * These run against the Vite dev server, so React's development warnings are
 * live and real framer-motion is in play. The unit tests mock framer-motion, so
 * this is the only place that can catch a regression in how the widget's DOM is
 * wired to the animation library.
 */
test.describe("chat widget", () => {
  test("opens, ignores clicks inside, closes on a click outside", async ({ page }) => {
    await page.goto("/");

    const launcher = page.getByRole("button", { name: /ask radcrew/i });
    const panel = page.getByRole("dialog", { name: /radcrew chat/i });

    await launcher.click();
    await expect(panel).toBeVisible();

    // Hit-testing is by data attribute, so this also proves the attribute
    // survives framer-motion's prop forwarding.
    await panel.getByPlaceholder(/ask anything about radcrew/i).click();
    await expect(panel).toBeVisible();

    await page.locator("footer").click({ position: { x: 5, y: 5 } });
    await expect(panel).toBeHidden();
  });

  test("logs no React ref warning when the panel opens", async ({ page }) => {
    const warnings: string[] = [];
    page.on("console", (message) => {
      const text = message.text();
      if (text.includes("`ref` is not a prop") || text.includes("Accessing element.ref")) {
        warnings.push(text);
      }
    });

    await page.goto("/");
    await page.getByRole("button", { name: /ask radcrew/i }).click();
    await expect(page.getByRole("dialog", { name: /radcrew chat/i })).toBeVisible();

    expect(warnings).toEqual([]);
  });
});
