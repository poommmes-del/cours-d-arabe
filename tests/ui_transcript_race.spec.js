const { test, expect } = require("@playwright/test");

test("latest transcript response wins", async ({ page }) => {
  let requestNumber = 0;
  let releaseFirst = () => {};
  let markFirstStarted = () => {};
  let markFirstFinished = () => {};
  const firstGate = new Promise((resolve) => {
    releaseFirst = resolve;
  });
  const firstStarted = new Promise((resolve) => {
    markFirstStarted = resolve;
  });
  const firstFinished = new Promise((resolve) => {
    markFirstFinished = resolve;
  });

  await page.addInitScript(() => {
    const originalFetch = window.fetch;
    window.__transcriptTextReads = 0;
    window.fetch = async (...args) => {
      const response = await originalFetch.apply(window, args);
      const resource = args[0];
      const url = typeof resource === "string" ? resource : resource.url;
      if (!url.includes("/transcriptions-deepgram/")) {
        return response;
      }
      const originalText = response.text.bind(response);
      response.text = async () => {
        const body = await originalText();
        window.__transcriptTextReads += 1;
        return body;
      };
      return response;
    };
  });

  await page.route("**/transcriptions-deepgram/**", async (route) => {
    const current = ++requestNumber;
    if (current === 1) {
      markFirstStarted();
      await firstGate;
    }
    await route.fulfill({
      status: 200,
      contentType: "text/markdown; charset=utf-8",
      body: `## Transcription\n\n${current === 1 ? "FIRST_RESPONSE" : "SECOND_RESPONSE"}\n\n## Segments\n\n[00:00 - 00:01] ${current === 1 ? "FIRST_SEGMENT" : "SECOND_SEGMENT"}\n`,
    });
    if (current === 1) {
      markFirstFinished();
    }
  });

  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await page.locator(".course-tile").first().click();
  await firstStarted;
  await page.locator("#lessonSelect").selectOption({ index: 1 });
  await expect(page.locator("#transcriptText")).toHaveText("SECOND_RESPONSE");
  const segmentTexts = page.locator("#segmentList .segment-button span:last-child");
  await expect(segmentTexts).toHaveCount(1);
  await expect(segmentTexts).toHaveText(["SECOND_SEGMENT"]);
  await expect(page.locator("#segmentList")).not.toContainText("FIRST_SEGMENT");

  releaseFirst();
  await firstFinished;
  await expect.poll(() => page.evaluate(() => window.__transcriptTextReads)).toBe(2);
  await page.evaluate(() => new Promise((resolve) => setTimeout(resolve, 0)));
  await expect(segmentTexts).toHaveCount(1);
  await expect(segmentTexts).toHaveText(["SECOND_SEGMENT"]);
  await expect(page.locator("#segmentList")).not.toContainText("FIRST_SEGMENT");
  await expect(page.locator("#transcriptText")).toHaveText("SECOND_RESPONSE");
});
