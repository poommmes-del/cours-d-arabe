#!/usr/bin/env node

const fs = require("node:fs/promises");
const path = require("node:path");
const { chromium } = require("@playwright/test");

const root = path.resolve(__dirname, "..");
const shamelaRoot = path.join(root, "livres", "shamela");
const force = process.argv.includes("--force");

async function walk(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walk(fullPath)));
    } else if (entry.name === "book.html") {
      files.push(fullPath);
    }
  }
  return files;
}

function cleanBookHtml(html) {
  return String(html ?? "")
    .replace(/(<h[1-6][^>]*>)\s*#+\s*/g, "$1")
    .replace(/<a[^>]*class="[^"]*btn_tag[^"]*"[^>]*>.*?<\/a>/gs, "");
}

function bookDocument(body) {
  return `<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <style>
    @page { size: A4; margin: 14mm 15mm; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #171914;
      font-family: "Noto Naskh Arabic", "Amiri", "Scheherazade New", "Segoe UI", Tahoma, sans-serif;
      direction: rtl;
    }
    .book-page {
      width: 100%;
      min-height: 100%;
    }
    h1, h2, h3 {
      margin: 0 0 18px;
      color: #0c4f48;
      font-weight: 800;
      line-height: 1.8;
      text-align: center;
      break-after: avoid;
    }
    h2 {
      border-bottom: 1px solid #d8d1c2;
      padding-bottom: 8px;
      font-size: 24px;
    }
    p {
      margin: 0 0 12px;
      font-size: 18px;
      line-height: 2.05;
      text-align: justify;
    }
    .c4, .c5 { color: #0a6b61; font-weight: 800; }
    .c1 { color: #7f3b18; font-weight: 700; }
    hr {
      border: 0;
      border-top: 1px solid #d8d1c2;
      margin: 24px 0 14px;
    }
    .hamesh {
      color: #5f6259;
      font-size: 15px;
    }
  </style>
</head>
<body>
  <main class="book-page">${body}</main>
</body>
</html>`;
}

async function shouldGenerate(input, output) {
  if (force) {
    return true;
  }
  try {
    const [inputStat, outputStat] = await Promise.all([fs.stat(input), fs.stat(output)]);
    return outputStat.mtimeMs < inputStat.mtimeMs;
  } catch {
    return true;
  }
}

async function main() {
  const books = await walk(shamelaRoot);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1240, height: 1754 } });
  let generated = 0;

  for (const bookPath of books) {
    const output = bookPath.replace(/\.html$/u, ".pdf");
    if (!(await shouldGenerate(bookPath, output))) {
      continue;
    }
    const html = await fs.readFile(bookPath, "utf8");
    await page.setContent(bookDocument(cleanBookHtml(html)), { waitUntil: "load" });
    await page.pdf({
      path: output,
      format: "A4",
      printBackground: true,
      margin: { top: "12mm", right: "13mm", bottom: "14mm", left: "13mm" },
    });
    generated += 1;
    console.log(path.relative(root, output));
  }

  await browser.close();
  console.log(`generated=${generated} total=${books.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
