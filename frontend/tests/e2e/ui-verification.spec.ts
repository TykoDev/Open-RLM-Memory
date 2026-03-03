import { expect, test } from "@playwright/test";

const BASE_URL = "http://localhost:3000";

const mockMemories = {
  results: [
    {
      id: "1",
      content: "User prefers dark mode UI.",
      type: "preference",
      tags: ["ui", "theme"],
      created_at: new Date().toISOString(),
      score: 0.9,
      metadata: {},
    },
    {
      id: "2",
      content: "Meeting with engineering team at 10 AM.",
      type: "event",
      tags: ["work", "meeting"],
      created_at: new Date().toISOString(),
      score: 0.8,
      metadata: {},
    },
  ],
  total_results: 2,
};

test.describe("Frontend UI Verification", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem("memory-namespace", "local");
    });
  });

  test("Root Dashboard loads correctly", async ({ page }) => {
    await page.goto(BASE_URL);

    await expect(page).toHaveTitle(/RLM MCP Memory/i);
    await expect(page.getByText("Welcome, local")).toBeVisible();
    await expect(page.getByPlaceholder("Ask your memory...")).toBeVisible();
  });

  test("Namespace login routes to dashboard", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await expect(page.getByText("Choose Memory Namespace")).toBeVisible();
    await page.getByLabel("Namespace").fill("local");
    await page.getByRole("button", { name: "Continue" }).click();

    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    await expect(page.getByText("Welcome, local")).toBeVisible();
  });

  test("Memory Page interaction", async ({ page }) => {
    await page.route("**/api/v1/memory/search", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockMemories),
      });
    });

    await page.goto(`${BASE_URL}/memory`);

    await expect(page.getByText("Knowledge Management")).toBeVisible();
    await expect(page.getByText("User prefers dark mode UI.")).toBeVisible();
  });
});
