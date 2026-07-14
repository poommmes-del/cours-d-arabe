const { test, expect } = require("@playwright/test");

test("ajroumiya exposes complete transcript-first modules", async ({ page }) => {
  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await page.locator("#searchInput").fill("ajroumiya");
  const ajroumiyaCourse = page.locator("#homeGrid .course-tile");
  await expect(ajroumiyaCourse).toHaveCount(1);
  await ajroumiyaCourse.click();
  const modules = page.locator("#moduleGrid .module-tile");
  const count = await modules.count();
  expect(count).toBeGreaterThanOrEqual(25);
  expect(count).toBeLessThanOrEqual(35);

  for (const index of [0, Math.floor(count / 2), count - 1]) {
    await modules.nth(index).click();
    await expect(page.locator("#courseContent")).toContainText("الهدف");
    await expect(page.locator("#courseContent")).toContainText("خلاصة للحفظ");
    await page.locator('[data-tab="quiz"]').click();
    const questions = page.locator("#quizList .question-card");
    const questionCount = await questions.count();
    expect(questionCount).toBeGreaterThanOrEqual(8);
    expect(questionCount).toBeLessThanOrEqual(10);
    await questions.first().locator(".answer-toggle").click();
    await expect(questions.first().locator(".question-answer")).toBeVisible();
  }
});

test("ajroumiya module selection follows mapped audio", async ({ page }) => {
  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await page.locator("#searchInput").fill("ajroumiya");
  await page.locator("#homeGrid .course-tile").click();

  await page.locator("#moduleGrid .module-tile").nth(1).click();

  await expect(page.locator("#lessonSelect option:checked")).toHaveText("2. 01:11:56");
  await expect(page.locator("#audioPlayer")).toHaveAttribute(
    "src",
    "../audios-opus/ajroumiya/002.opus",
  );
  await expect
    .poll(() => page.locator("#audioPlayer").evaluate((audio) => audio.currentTime))
    .toBeGreaterThanOrEqual(6);
});
