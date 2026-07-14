const { test, expect } = require("@playwright/test");

const allCourseIds = [
  "ajroumiya",
  "moutammima",
  "qatr-nada",
  "qawaid-i3raab-sa3di",
  "qawaid-i3raab-zawawi",
  "mawsil-toullab",
  "shoudhour-dhahab",
  "alfiya-nahw",
  "moulakhas-sarfi",
  "nadhm-maqsoud",
  "alfiya-sarf",
  "laamiya-af3al",
  "dourous-balagha",
  "maani-we-bayan",
];
const requestedIds = process.env.COURSE_IDS
  ? process.env.COURSE_IDS.split(",").map((identifier) => identifier.trim()).filter(Boolean)
  : allCourseIds;
const contentHeadings = [
  "الهدف",
  "قبل أن تبدأ",
  "شرح المسألة",
  "القاعدة",
  "لماذا؟",
  "أمثلة متدرجة",
  "تحليل خطوة خطوة",
  "خطأ شائع",
  "تدريب موجه",
  "تدريب مستقل",
  "خلاصة للحفظ",
];

for (const courseId of requestedIds) {
  test(`${courseId} exposes transcript-first quality on sampled modules`, async ({ page }) => {
    await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
    await page.locator("#searchInput").fill(courseId);
    const courseTile = page.locator("#homeGrid .course-tile");
    await expect(courseTile).toHaveCount(1);
    await courseTile.click();

    const modules = page.locator("#moduleGrid .module-tile");
    const moduleCount = await modules.count();
    expect(moduleCount).toBeGreaterThan(0);
    const sampleIndexes = [...new Set([0, Math.floor(moduleCount / 2), moduleCount - 1])];

    for (const index of sampleIndexes) {
      await modules.nth(index).click();
      const expectedHeadings = [
        ...contentHeadings,
        index === 0 ? "تشخيص قبلي" : "مراجعة تراكمية",
      ];
      const renderedHeadings = page.locator("#courseContent .markdown-body h5");
      expect(await renderedHeadings.allTextContents()).toEqual(expectedHeadings);

      const quizTab = page.locator('[data-tab="quiz"]');
      await expect(quizTab).toBeVisible();
      await quizTab.click();
      await expect(page.locator("#quizList")).toBeVisible();
      const questions = page.locator("#quizList .question-card");
      const questionCount = await questions.count();
      expect(questionCount).toBeGreaterThanOrEqual(8);
      expect(questionCount).toBeLessThanOrEqual(10);
      const firstQuestion = questions.first();
      await firstQuestion.locator(".answer-toggle").click();
      await expect(firstQuestion.locator(".question-answer")).toBeVisible();
    }
  });
}
