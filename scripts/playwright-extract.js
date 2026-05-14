#!/usr/bin/env node
/* Replacement for both TabStack (markdown extract) and screenshot.
 * Usage:
 *   node playwright-extract.js <url> --markdown --output file.md
 *   node playwright-extract.js <url> --screenshot --output file.png [--full]
 *   node playwright-extract.js <url> --scrape --output file.json   (structured DOM)
 */
const { chromium } = require('playwright');
const fs = require('fs');
const TurndownService = require('turndown');

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: playwright-extract.js <url> [--markdown|--screenshot|--scrape] [--full] [--output path]');
    process.exit(1);
  }
  const url = args[0];
  const flags = {
    markdown: args.includes('--markdown'),
    screenshot: args.includes('--screenshot'),
    scrape: args.includes('--scrape'),
    full: args.includes('--full'),
  };
  const oi = args.indexOf('--output');
  const output = oi >= 0 ? args[oi + 1] : null;

  const browser = await chromium.launch({ headless: true });
  try {
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
      viewport: { width: 1440, height: 900 },
    });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(2500); // let JS settle

    if (flags.screenshot) {
      const out = output || 'screenshot.png';
      await page.screenshot({ path: out, fullPage: !!flags.full });
      console.log(`Screenshot saved: ${out}`);
    }
    if (flags.markdown) {
      const html = await page.evaluate(() => {
        // strip noisy elements
        ['script','style','noscript','iframe','svg','header nav','footer'].forEach(sel => {
          document.querySelectorAll(sel).forEach(el => el.remove());
        });
        return document.body.innerHTML;
      });
      const td = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
      const md = td.turndown(html).replace(/\n{3,}/g, '\n\n').trim();
      const meta = `# ${await page.title()}\n\nURL: ${url}\n\n---\n\n`;
      if (output) {
        fs.writeFileSync(output, meta + md);
        console.log(`Markdown saved: ${output} (${md.length} chars)`);
      } else {
        process.stdout.write(meta + md);
      }
    }
    if (flags.scrape) {
      const data = await page.evaluate(() => ({
        title: document.title,
        url: location.href,
        h1: Array.from(document.querySelectorAll('h1')).map(e => e.innerText.trim()).slice(0, 5),
        h2: Array.from(document.querySelectorAll('h2')).map(e => e.innerText.trim()).slice(0, 20),
        ctaButtons: Array.from(document.querySelectorAll('a,button')).map(e => e.innerText.trim()).filter(t => t && t.length < 60 && /купить|заказ|начать|попробовать|записаться|узнать|try|start|buy|sign up|get|join|book/i.test(t)).slice(0, 15),
        images: Array.from(document.images).map(i => i.alt || '').filter(Boolean).slice(0, 20),
        priceMentions: (document.body.innerText.match(/\$\s?\d{1,5}(?:[.,]\d{2})?|\d{1,5}\s?(?:₽|руб|RUB|EUR|€)/g) || []).slice(0, 20),
      }));
      const out = output || null;
      const j = JSON.stringify(data, null, 2);
      if (out) { fs.writeFileSync(out, j); console.log(`Scrape saved: ${out}`); }
      else console.log(j);
    }
  } finally {
    await browser.close();
  }
}

main().catch(e => { console.error(e); process.exit(1); });
