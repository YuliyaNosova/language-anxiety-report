#!/usr/bin/env node
/**
 * Meta Ad Library scraper with scroll/pagination.
 * Scrolls to load more ads until target count or no new ads appear.
 * Usage: node meta-ads-scroll.js "BrandName" --country US --limit 50 --output data/raw_ads_brand.json
 */
const { chromium } = require('playwright');
const fs = require('fs');

async function extractAds(page) {
  return page.evaluate(() => {
    const results = [];
    const seen = new Set();

    // Find all divs containing "Started running on"
    const allDivs = Array.from(document.querySelectorAll('div'));
    for (const div of allDivs) {
      const text = div.innerText || '';
      if (!text.includes('Started running on')) continue;
      if (text.length < 30 || text.length > 8000) continue;
      // Must be a leaf-ish container (not a huge parent)
      const childrenWithText = Array.from(div.children).filter(c => (c.innerText||'').includes('Started running on'));
      if (childrenWithText.length > 0) continue; // Skip parent wrappers

      // Extract Library ID
      const libMatch = text.match(/Library ID:\s*(\d+)/);
      const libId = libMatch ? libMatch[1] : null;
      if (!libId || seen.has(libId)) continue;
      seen.add(libId);

      // Extract date
      const dateMatch = text.match(/Started running on (\d{1,2} [A-Z][a-z]{2} \d{4})/);
      const dateMatch2 = !dateMatch && text.match(/Started running on ([A-Z][a-z]+ \d{1,2}, \d{4})/);
      const startDateRaw = dateMatch ? dateMatch[1] : (dateMatch2 ? dateMatch2[1] : null);

      // Media type
      const videos = div.querySelectorAll('video');
      const imgs = div.querySelectorAll('img');
      let mediaType = 'unknown';
      if (videos.length > 0) mediaType = 'video';
      else if (imgs.length > 1) mediaType = 'carousel';
      else if (imgs.length === 1) mediaType = 'image';

      // Landing URLs (external links)
      const links = Array.from(div.querySelectorAll('a[href]'))
        .map(a => a.href)
        .filter(h => h && !h.includes('facebook.com') && !h.includes('javascript:') && !h.startsWith('#'));

      // Ad copy lines
      const lines = text.split('\n').map(l => l.trim()).filter(l => {
        if (!l || l.length < 8) return false;
        if (/^Library ID:/.test(l)) return false;
        if (/^\d+ ads? use/.test(l)) return false;
        if (/^Started running on/.test(l)) return false;
        if (/^See (ad details|summary)/.test(l)) return false;
        if (/^(About this ad|Sponsored|Ad|Open Drop-down|Platforms|Categories|EU transparency)$/.test(l)) return false;
        if (/^[​\s]+$/.test(l)) return false;
        return true;
      });

      results.push({
        library_id: libId,
        start_date_raw: startDateRaw,
        media_type: mediaType,
        ad_copy: lines.slice(0, 6).join(' | '),
        landing_urls: links.slice(0, 3),
        raw_text: text.slice(0, 600),
      });
    }
    return results;
  });
}

async function scrape(brand, country, limit, outputPath) {
  const url = `https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=${country}&q=${encodeURIComponent(brand)}&search_type=keyword_unordered&media_type=all`;
  const browser = await chromium.launch({ headless: true });
  const allAds = new Map(); // library_id -> ad

  try {
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
      viewport: { width: 1440, height: 900 },
      locale: 'en-US',
    });
    const page = await ctx.newPage();

    console.log(`Loading Meta Ad Library for "${brand}"...`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    // Accept cookies if present
    try {
      for (const sel of ['button:has-text("Allow all cookies")', 'button:has-text("Accept All")', '[data-testid="cookie-policy-manage-dialog-accept-button"]']) {
        const btn = page.locator(sel);
        if (await btn.count() > 0) { await btn.first().click(); await page.waitForTimeout(1500); break; }
      }
    } catch(e) {}

    // Scroll loop to load more ads
    let prevCount = 0;
    let noNewRounds = 0;
    for (let round = 0; round < 12 && allAds.size < limit; round++) {
      const batch = await extractAds(page);
      for (const ad of batch) {
        if (!allAds.has(ad.library_id)) allAds.set(ad.library_id, ad);
      }
      console.log(`  Round ${round+1}: ${allAds.size} unique ads`);

      if (allAds.size === prevCount) {
        noNewRounds++;
        if (noNewRounds >= 3) { console.log('  No new ads for 3 rounds, stopping'); break; }
      } else {
        noNewRounds = 0;
      }
      prevCount = allAds.size;

      // Scroll down
      await page.evaluate(() => window.scrollBy(0, 1500));
      await page.waitForTimeout(2500);

      // Click "See more" / "Load more" buttons if present
      try {
        const more = page.locator('div[role="button"]:has-text("See more results"), button:has-text("Show more")');
        if (await more.count() > 0) { await more.first().click(); await page.waitForTimeout(2000); }
      } catch(e) {}
    }

    // Screenshot
    const ssDir = '/Users/yuliyanosova/vibecoding/research/language-anxiety/data/screenshots';
    if (!fs.existsSync(ssDir)) fs.mkdirSync(ssDir, { recursive: true });
    await page.screenshot({ path: `${ssDir}/meta_${brand.toLowerCase().replace(/\s+/g,'_')}.png`, fullPage: false });

  } finally {
    await browser.close();
  }

  const ads = Array.from(allAds.values());
  console.log(`Total unique ads: ${ads.length}`);

  if (outputPath) {
    fs.writeFileSync(outputPath, JSON.stringify(ads, null, 2));
    console.log(`Saved to ${outputPath}`);
  }
  return ads;
}

async function main() {
  const args = process.argv.slice(2);
  const brand = args[0] || 'TalkPal';
  const ci = args.indexOf('--country'); const country = ci >= 0 ? args[ci+1] : 'US';
  const li = args.indexOf('--limit');   const limit = li >= 0 ? parseInt(args[li+1]) : 50;
  const oi = args.indexOf('--output');  const output = oi >= 0 ? args[oi+1] : null;
  await scrape(brand, country, limit, output);
}

main().catch(e => { console.error(e.message); process.exit(1); });
