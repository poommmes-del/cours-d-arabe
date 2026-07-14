const { test, expect } = require("@playwright/test");

test("book resources open inside Matn Charh tab", async ({ page }) => {
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      errors.push(message.text());
    }
  });
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("http://127.0.0.1:8766/site/", { waitUntil: "networkidle" });
  await page.locator(".course-tile").first().click();
  await page.locator("[data-tab='resources']").click();

  await expect(page.locator("#bookViewer")).toHaveCount(0);
  await expect(page.locator("#resourcesTab iframe, #resourcesTab .book-text")).toHaveCount(0);
  await expect(page.locator(".resource-viewer-button").first()).toContainText("Consulter");
  await expect(page.locator(".resource-item .resource-viewer-button")).toHaveCount(3);
  await expect(page.locator(".resource-item .resource-viewer-button").nth(0)).toContainText("ابن آجروم");
  await expect(page.locator(".resource-item .resource-viewer-button").nth(1)).toContainText("ابن عثيمين");
  await expect(page.locator(".resource-item .resource-viewer-button").nth(2)).toContainText("الخضير");
  await expect(page.locator(".resource-item .resource-viewer-button").first()).toHaveAttribute("href", /\.pdf$/);
  for (const href of await page.locator(".resource-item .resource-viewer-button").evaluateAll((links) => links.map((link) => link.getAttribute("href")))) {
    expect(href).toContain("../livres/pdf/");
  }
  await expect(page.locator(".resource-item .resource-viewer-button").first()).toHaveAttribute("target", "_blank");
  await expect(page.locator(".resource-item .resource-links a:not(.resource-viewer-button)")).toHaveCount(0);
  await expect(page.locator(".resource-list")).not.toContainText("Shamela · url");
  await expect(page.locator(".resource-list")).not.toContainText("Local · md");
  await expect(page.locator(".resource-list")).not.toContainText("OCR · txt");

  await page.screenshot({ path: "/tmp/cours-arabe-resources.png", fullPage: false });
  expect(errors).toEqual([]);
});
