#!/usr/bin/env node
/**
 * Meta Ad Library scraper: parses full body.innerText, extracts all ad blocks,
 * then filters by advertiser name or keyword.
 *
 * Usage:
 *   node meta-ads-bodytext.js --query "TalkPal" --advertiser "TalkPal" --country US --limit 30 --output data/raw_ads_talkpal.json
 *
 * --query: search term for Meta Ad Library URL
 * --advertiser: filter extracted ads by advertiser name (substring match, case-insensitive)
 *               if omitted, keep all ads
 */
const { chromium } = require('playwright');
const fs = require('fs');

function parseAdsFromText(bodyText, advertiserFilter) {
  // Each ad block looks like:
  // [Active|Inactive]
  // Library ID: NNNN
  // [date range or "Started running on ..."]
  // Platforms
  // ...
  // [PageName]
  // Sponsored
  // [ad copy text]
  // ...
  // (next ad or end)

  const ads = [];
  const seen = new Set();

  // Split by Library ID anchors
  const blocks = bodyText.split(/(?=(?:Active|Inactive)\s*\n.*?Library ID:)/);

  for (const block of blocks) {
    const libMatch = block.match(/Library ID:\s*(\d+)/);
    if (!libMatch) continue;
    const libId = libMatch[1];
    if (seen.has(libId)) continue;
    seen.add(libId);

    // Status
    const isActive = /^Active/m.test(block);

    // Date range: "1 Dec 2025 - 3 Apr 2026" or "Started running on Dec 26, 2025"
    let startDate = null;
    const dateRange = block.match(/(\d{1,2} [A-Z][a-z]+ \d{4})\s*[-–]\s*(\d{1,2} [A-Z][a-z]+ \d{4}|\d{4}-\d{2}-\d{2})/);
    const startedRunning = block.match(/Started running on ([A-Z][a-z]+ \d{1,2}, \d{4}|\d{1,2} [A-Z][a-z]+ \d{4})/);
    if (dateRange) {
      startDate = dateRange[1];
    } else if (startedRunning) {
      startDate = startedRunning[1];
    }

    // Parse startDate to ISO
    let startDateISO = null;
    if (startDate) {
      const fmts = [
        [/(\d{1,2}) ([A-Z][a-z]+) (\d{4})/, (m) => `${m[3]}-${monthNum(m[2])}-${m[1].padStart(2,'0')}`],
        [/([A-Z][a-z]+) (\d{1,2}), (\d{4})/, (m) => `${m[3]}-${monthNum(m[1])}-${m[2].padStart(2,'0')}`],
      ];
      for (const [re, fn] of fmts) {
        const m = startDate.match(re);
        if (m) { startDateISO = fn(m); break; }
      }
    }

    // Advertiser: line before "Sponsored"
    const sponsoredIdx = block.indexOf('\nSponsored\n');
    let advertiser = '';
    let adCopy = '';
    if (sponsoredIdx >= 0) {
      const before = block.slice(0, sponsoredIdx).trim().split('\n');
      advertiser = before[before.length - 1].trim();
      adCopy = block.slice(sponsoredIdx + '\nSponsored\n'.length).trim();
    } else {
      // Fallback: look for pagename after platforms section
      const afterPlatforms = block.replace(/.*?Platforms[\s\S]*?(?=\n[A-Z])/s, '');
      const lines = afterPlatforms.split('\n').map(l => l.trim()).filter(Boolean);
      advertiser = lines[0] || '';
      adCopy = lines.slice(1).join(' ');
    }

    // Filter by advertiser if specified
    if (advertiserFilter && !advertiser.toLowerCase().includes(advertiserFilter.toLowerCase())) {
      continue;
    }

    // Clean ad copy
    const skipRe = /^(See (ad|summary) details|About this ad|Open Drop|Platforms|EU transparency|\d+ ads? use|0:00|​)/i;
    const copyLines = adCopy.split('\n')
      .map(l => l.trim())
      .filter(l => l.length >= 5 && !skipRe.test(l) && !/^[​\s]+$/.test(l));
    const cleanCopy = copyLines.slice(0, 8).join('\n').slice(0, 600);

    // Media type heuristic from copy
    let mediaType = 'unknown';
    if (block.includes('0:00 / 0:00') || /video/i.test(block)) mediaType = 'video';
    else if (/carousel|swipe/i.test(block)) mediaType = 'carousel';

    ads.push({
      library_id: libId,
      advertiser,
      is_active: isActive,
      start_date_raw: startDate,
      start_date: startDateISO,
      media_type: mediaType,
      ad_copy: cleanCopy,
      landing_urls: [],
      raw_block: block.slice(0, 800),
    });
  }

  return ads;
}

function monthNum(name) {
  const months = { Jan:'01',Feb:'02',Mar:'03',Apr:'04',May:'05',Jun:'06',
                   Jul:'07',Aug:'08',Sep:'09',Oct:'10',Nov:'11',Dec:'12',
                   January:'01',February:'02',March:'03',April:'04',June:'06',
                   July:'07',August:'08',September:'09',October:'10',November:'11',December:'12' };
  return months[name] || '01';
}

async function scrape(query, advertiser, country, limit, outputPath) {
  const url = `https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=${country}&q=${encodeURIComponent(query)}&search_type=keyword_unordered&media_type=all`;
  const browser = await chromium.launch({ headless: true });
  let allAds = [];

  try {
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
      viewport: { width: 1440, height: 900 }, locale: 'en-US',
    });
    const page = await ctx.newPage();
    console.log(`Loading: ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    const seenIds = new Set();
    let noNewRounds = 0;

    for (let round = 0; round < 15 && allAds.length < limit; round++) {
      const bodyText = await page.evaluate(() => document.body.innerText);
      const batch = parseAdsFromText(bodyText, advertiser).filter(a => !seenIds.has(a.library_id));
      for (const a of batch) seenIds.add(a.library_id);
      allAds.push(...batch);
      console.log(`  Round ${round+1}: +${batch.length} new (total ${allAds.length}) | page_len=${bodyText.length}`);

      if (batch.length === 0) {
        noNewRounds++;
        if (noNewRounds >= 3) { console.log('  No new ads, stopping'); break; }
      } else {
        noNewRounds = 0;
      }

      await page.evaluate(() => window.scrollBy(0, 2500));
      await page.waitForTimeout(3000);

      try {
        const btn = page.locator('div[role="button"]:has-text("See more results"), button:has-text("See more")');
        if (await btn.count() > 0) { await btn.first().click(); await page.waitForTimeout(2000); }
      } catch(e) {}
    }

    // Screenshot
    const ssDir = '/Users/yuliyanosova/vibecoding/research/language-anxiety/data/screenshots';
    if (!fs.existsSync(ssDir)) fs.mkdirSync(ssDir, { recursive: true });
    const ssName = (advertiser || query).toLowerCase().replace(/[^a-z0-9]/g,'_');
    await page.screenshot({ path: `${ssDir}/meta_${ssName}.png` });

  } finally {
    await browser.close();
  }

  console.log(`Total: ${allAds.length} ads for advertiser="${advertiser || 'all'}"`);
  if (outputPath) {
    fs.writeFileSync(outputPath, JSON.stringify(allAds, null, 2));
    console.log(`Saved to ${outputPath}`);
  }
  return allAds;
}

async function main() {
  const args = process.argv.slice(2);
  const qi = args.indexOf('--query');       const query      = qi >= 0 ? args[qi+1] : args[0] || 'TalkPal';
  const ai = args.indexOf('--advertiser');  const advertiser = ai >= 0 ? args[ai+1] : '';
  const ci = args.indexOf('--country');     const country    = ci >= 0 ? args[ci+1] : 'US';
  const li = args.indexOf('--limit');       const limit      = li >= 0 ? parseInt(args[li+1]) : 30;
  const oi = args.indexOf('--output');      const output     = oi >= 0 ? args[oi+1] : null;
  await scrape(query, advertiser, country, limit, output);
}

main().catch(e => { console.error(e.message); process.exit(1); });
