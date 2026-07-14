const { test, expect } = require("@playwright/test");

test("quiz flow works", async ({ page }) => {
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      errors.push(message.text());
    }
  });
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await expect(page.locator(".course-tile")).toHaveCount(14);

  await page.locator(".course-tile").first().click();
  await page.locator("[data-tab='quiz']").click();

  await expect(page.locator(".question-card").first()).toBeVisible();
  await page.locator(".question-card").first().locator(".answer-toggle").click();
  await expect(page.locator(".question-answer").first()).toBeVisible();
  await expect(page.locator(".question-answer").first()).toContainText(/Corrig/);
  await expect(page.locator(".quiz-toggle")).toHaveCount(0);
  await expect(page.locator("text=Valider")).toHaveCount(0);
  await expect(page.locator("text=Validée")).toHaveCount(0);

  await page.screenshot({ path: "/tmp/cours-arabe-quiz.png", fullPage: false });
  expect(errors).toEqual([]);
});
