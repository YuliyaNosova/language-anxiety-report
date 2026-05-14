#!/usr/bin/env node
/**
 * Meta Ad Library scraper via Playwright with scroll and dedup.
 * Usage: node meta-ads-playwright.js "BrandName" --country US --limit 40 --output path.json
 */
const { chromium } = require('playwright');
const fs = require('fs');

async function extractAds(page, knownIds) {
  return page.evaluate((knownArr) => {
    const known = new Set(knownArr);
    const results = [];

    // Strategy: find ALL divs with "Started running", sort by size ASC,
    // take smallest unique-by-libId ones (avoids processing huge parent containers)
    const candidates = [];
    for (const div of document.querySelectorAll('div')) {
      const t = div.innerText || '';
      if (!t.includes('Started running') || t.length < 50 || t.length > 4000) continue;
      candidates.push({ div, len: t.length, text: t });
    }
    // Sort by text length ascending — smallest = most specific container
    candidates.sort((a, b) => a.len - b.len);

    const processedIds = new Set(known);

    for (const { div, text } of candidates) {
      const libMatch = text.match(/Library ID:\s*(\d+)/);
      if (!libMatch) continue;
      const libId = libMatch[1];
      if (processedIds.has(libId)) continue;
      processedIds.add(libId);

      // Date: "Dec 26, 2025" or "26 Dec 2025" or "January 15, 2026"
      const d1 = text.match(/Started running on ([A-Z][a-z]+ \d{1,2}, \d{4})/);
      const d2 = text.match(/Started running on (\d{1,2} [A-Z][a-z]{2} \d{4})/);
      const startDateRaw = d1 ? d1[1] : (d2 ? d2[1] : null);

      // Media
      const vids = div.querySelectorAll('video');
      const imgs = div.querySelectorAll('img');
      let mediaType = 'unknown';
      if (vids.length > 0) mediaType = 'video';
      else if (imgs.length > 1) mediaType = 'carousel';
      else if (imgs.length === 1) mediaType = 'image';

      // Landing URLs
      const links = Array.from(div.querySelectorAll('a[href]'))
        .map(a => a.href)
        .filter(h => h && !h.includes('facebook.com') && !h.includes('javascript:') && !h.startsWith('#'));

      // Page name
      const fbLink = div.querySelector('a[href*="facebook.com/"]');
      const pageName = (fbLink ? fbLink.innerText : '').trim();

      // Ad copy
      const skipRe = /^(Library ID:|Started running|See (ad|summary)|About this ad|Sponsored$|^Ad$|Open Drop|Platforms|Categories|EU transparency|\d+ ads? use|Active$|Inactive$)/i;
      const copyLines = text.split('\n')
        .map(l => l.trim())
        .filter(l => l.length >= 10 && !skipRe.test(l) && !/^[​\s]+$/.test(l));

      results.push({
        library_id: libId,
        page_name: pageName,
        start_date_raw: startDateRaw,
        media_type: mediaType,
        ad_copy: copyLines.slice(0, 5).join(' | ').slice(0, 400),
        landing_urls: links.slice(0, 3),
        raw_text: text.slice(0, 500),
      });
    }
    return { ads: results, newKnown: Array.from(processedIds) };
  }, Array.from(knownIds));
}

async function scrape(brand, country, limit, outputPath) {
  const url = `https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=${country}&q=${encodeURIComponent(brand)}&search_type=keyword_unordered&media_type=all`;
  const browser = await chromium.launch({ headless: true });
  const allAds = [];
  let knownIds = new Set();

  try {
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
      viewport: { width: 1440, height: 900 }, locale: 'en-US',
    });
    const page = await ctx.newPage();

    console.log(`Loading Meta Ad Library for "${brand}" [${country}]...`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    // Accept cookies if present
    for (const sel of ['button:has-text("Allow all cookies")', 'button:has-text("Accept All")', '[data-testid="cookie-policy-manage-dialog-accept-button"]']) {
      try {
        const btn = page.locator(sel);
        if (await btn.count() > 0) { await btn.first().click(); await page.waitForTimeout(1500); break; }
      } catch(e) {}
    }
    await page.waitForTimeout(2000);

    let noNewRounds = 0;
    for (let round = 0; round < 15 && allAds.length < limit; round++) {
      const { ads: batch, newKnown } = await extractAds(page, knownIds);
      knownIds = new Set(newKnown);
      allAds.push(...batch);
      console.log(`  Round ${round+1}: +${batch.length} new (total ${allAds.length})`);

      if (batch.length === 0) {
        noNewRounds++;
        if (noNewRounds >= 3) { console.log('  No new ads, stopping'); break; }
      } else {
        noNewRounds = 0;
      }

      await page.evaluate(() => window.scrollBy(0, 2000));
      await page.waitForTimeout(2500);

      try {
        const moreBtn = page.locator('div[role="button"]:has-text("See more results")');
        if (await moreBtn.count() > 0) { await moreBtn.first().click(); await page.waitForTimeout(2000); }
      } catch(e) {}
    }

    // Screenshot
    const ssDir = '/Users/yuliyanosova/vibecoding/research/language-anxiety/data/screenshots';
    if (!fs.existsSync(ssDir)) fs.mkdirSync(ssDir, { recursive: true });
    await page.screenshot({ path: `${ssDir}/meta_${brand.toLowerCase().replace(/[^a-z0-9]/g,'_')}.png` });

  } finally {
    await browser.close();
  }

  console.log(`Total unique ads: ${allAds.length}`);
  if (outputPath) {
    fs.writeFileSync(outputPath, JSON.stringify(allAds, null, 2));
    console.log(`Saved to ${outputPath}`);
  }
  return allAds;
}

async function main() {
  const args = process.argv.slice(2);
  const brand  = args[0] || 'TalkPal';
  const ci = args.indexOf('--country'); const country = ci >= 0 ? args[ci+1] : 'US';
  const li = args.indexOf('--limit');   const limit   = li >= 0 ? parseInt(args[li+1]) : 40;
  const oi = args.indexOf('--output');  const output  = oi >= 0 ? args[oi+1] : null;
  await scrape(brand, country, limit, output);
}

main().catch(e => { console.error(e.message); process.exit(1); });
