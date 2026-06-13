import { defineConfig, devices } from "@playwright/test";

const FRONTEND_PORT = 8080;
const BASE_URL = `http://localhost:${FRONTEND_PORT}`;

/**
 * Optional escape hatch: if PLAYWRIGHT_CHROMIUM_PATH is set, launch that binary
 * instead of the build this Playwright version downloads. Useful on machines
 * that already have a Chromium but can't reach the Playwright CDN. Normally
 * unset — CI and most devs just run `npx playwright install chromium`.
 */
const CHROMIUM_PATH = process.env.PLAYWRIGHT_CHROMIUM_PATH;

/**
 * E2E config. Starts the Vite dev server and runs the specs in ./e2e against
 * the running frontend. These are smoke tests for the static landing page; they
 * do not require the backend. (A chat round-trip test would need a networked
 * backend + model and belongs in an environment that can run it.)
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        ...(CHROMIUM_PATH
          ? { launchOptions: { executablePath: CHROMIUM_PATH } }
          : {}),
      },
    },
  ],
  webServer: {
    command: "npm run dev",
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
