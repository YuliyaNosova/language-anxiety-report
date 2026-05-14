#!/usr/bin/env python3
"""Build creatives.json from raw Apify + Playwright body-text data."""
import json, re, os
from datetime import datetime, timezone

BASE = "/Users/yuliyanosova/vibecoding/research/language-anxiety"
today = datetime.now(timezone.utc).replace(tzinfo=None)
collection_date = today.strftime("%Y-%m-%d")


def parse_date_str(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ("%d %b %Y", "%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except:
            pass
    m = re.match(r'(\d{4}-\d{2}-\d{2})', s)
    return m.group(1) if m else None


def days_since(date_str):
    if not date_str:
        return None
    try:
        return (today - datetime.strptime(date_str, "%Y-%m-%d")).days
    except:
        return None


def extract_date_from_block(raw_block):
    """Extract start date from raw_block: 'Oct 9, 2025 - ...' or 'Started running on ...'"""
    for pat, fmt in [
        (r'([A-Z][a-z]+ \d{1,2}, \d{4})\s*[-\u2013]', "%b %d, %Y"),
        (r'(\d{1,2} [A-Z][a-z]+ \d{4})\s*[-\u2013]', "%d %b %Y"),
        (r'Started running on ([A-Z][a-z]+ \d{1,2}, \d{4})', "%b %d, %Y"),
        (r'Started running on (\d{1,2} [A-Z][a-z]+ \d{4})', "%d %b %Y"),
    ]:
        m = re.search(pat, raw_block)
        if m:
            try:
                from datetime import datetime as _dt
                return _dt.strptime(m.group(1), fmt).strftime("%Y-%m-%d")
            except: pass
    return None


def parse_bodytext_ad(item, brand):
    """Parse ad from meta-ads-bodytext.js format."""
    lib_id = item.get('library_id', 'unknown')
    raw_block = item.get('raw_block', '')
    start_date = (item.get('start_date') or
                  parse_date_str(item.get('start_date_raw')) or
                  extract_date_from_block(raw_block))
    days = days_since(start_date)
    return {
        "id": f"ad_{lib_id}",
        "brand": brand,
        "source": "meta_ad_library",
        "page_name": item.get('advertiser', brand),
        "text": (item.get('ad_copy') or '').strip()[:600],
        "media_type": item.get('media_type', 'unknown'),
        "format": "feed",
        "start_date": start_date,
        "is_active": item.get('is_active', True),
        "days_running": days,
        "is_evergreen": days is not None and days >= 30,
        "landing_url": (item.get('landing_urls') or [None])[0],
        "screenshot_path": None,
    }


def parse_apify_ad(item, brand):
    """Parse ad from Apify facebook-ads-scraper format."""
    archive_id = str(item.get('adArchiveID') or item.get('adArchiveId') or 'unknown')
    start_raw = item.get('startDateFormatted') or item.get('startDate') or ''
    end_raw = item.get('endDateFormatted') or item.get('endDate') or ''
    start_date = parse_date_str(start_raw[:10] if start_raw else None)
    days = days_since(start_date)
    is_active = bool(item.get('isActive', True))
    if end_raw and end_raw[:10] < collection_date:
        is_active = False
    snapshot = item.get('snapshot') or {}
    cards = snapshot.get('cards') or []
    media_type = 'unknown'
    if len(cards) > 1:
        media_type = 'carousel'
    elif snapshot.get('videos') or (cards and cards[0].get('video_sd_url')):
        media_type = 'video'
    elif snapshot.get('images') or (cards and cards[0].get('original_image_url')):
        media_type = 'image'
    body = snapshot.get('body') or {}
    body_text = body.get('text', '') if isinstance(body, dict) else str(body)
    title = snapshot.get('title') or (cards[0].get('title') if cards else '') or ''
    caption = snapshot.get('caption') or ''
    text = ' | '.join(filter(None, [body_text[:300], title[:100], caption[:100]]))
    link_url = snapshot.get('link_url') or (cards[0].get('link_url') if cards else None)
    return {
        "id": f"ad_{archive_id}",
        "brand": brand,
        "source": "meta_ad_library",
        "page_name": item.get('pageName', brand),
        "text": text[:600],
        "media_type": media_type,
        "format": "feed",
        "start_date": start_date,
        "is_active": is_active,
        "days_running": days,
        "is_evergreen": days is not None and days >= 30,
        "landing_url": link_url,
        "screenshot_path": None,
    }


def detect_format(item):
    if 'library_id' in item or 'ad_copy' in item:
        return 'bodytext'
    if 'adArchiveID' in item or 'adArchiveId' in item or 'startDateFormatted' in item:
        return 'apify'
    return 'bodytext'


def get_dedup_id(item):
    if 'library_id' in item:
        return item['library_id']
    return str(item.get('adArchiveID') or item.get('adArchiveId') or '')


# Brand -> list of source files
brand_sources = {
    "TalkPal": [
        (f"{BASE}/data/raw_ads_talkpal.json",),
    ],
    "Speak": [
        (f"{BASE}/data/raw_ads_speak.json",),
    ],
    "Cambly": [
        (f"{BASE}/data/raw_ads_cambly.json",),
    ],
    "AntiShkola": [
        (f"{BASE}/data/raw_ads_antishkola.json",),
    ],
    "Lindsay": [],
}

by_competitor = {}
all_landing_urls = {}
total_creatives = 0

for brand, sources in brand_sources.items():
    if not sources:
        by_competitor[brand] = {
            "total_ads": 0, "active_ads": 0, "evergreen_ads": 0,
            "note": "No paid Meta ads found. Primary channel: YouTube/SEO/Instagram (organic). Speaking Confidence Challenge is product-led growth.",
            "creatives": []
        }
        continue

    seen_ids = set()
    ads = []
    for (filepath,) in sources:
        if not os.path.exists(filepath):
            print(f"  WARNING: {filepath} not found")
            continue
        with open(filepath) as f:
            raw_data = json.load(f)
        for item in raw_data:
            uid = get_dedup_id(item)
            if uid and uid in seen_ids:
                continue
            if uid:
                seen_ids.add(uid)
            fmt = detect_format(item)
            ad = parse_apify_ad(item, brand) if fmt == 'apify' else parse_bodytext_ad(item, brand)
            ads.append(ad)
            if ad['landing_url']:
                url = ad['landing_url']
                if url not in all_landing_urls:
                    all_landing_urls[url] = {"brand": brand, "url": url, "ad_count": 0}
                all_landing_urls[url]["ad_count"] += 1

    active = sum(1 for a in ads if a['is_active'])
    evergreen = sum(1 for a in ads if a['is_evergreen'])
    total_creatives += len(ads)

    by_competitor[brand] = {
        "total_ads": len(ads),
        "active_ads": active,
        "evergreen_ads": evergreen,
        "creatives": ads,
    }

tiktok_top_ads = [{
    "industry": "Education / Language Learning",
    "region": "US",
    "description": "TikTok Creative Center top ads screenshot (Education, 7-day, US). Brand-specific search requires manual Creative Center filtering.",
    "screenshot_path": "data/screenshots/tiktok_top_ads.png",
}]

output = {
    "collection_date": collection_date,
    "competitors_processed": 5,
    "total_creatives": total_creatives,
    "data_sources": {
        "meta_apify_succeeded": ["Cambly (71 ads via Apify facebook-ads-scraper)"],
        "meta_playwright_bodytext": ["TalkPal (5)", "Speak (6)", "AntiShkola (23)"],
        "no_paid_ads": ["Lindsay Does Languages — organic YouTube/SEO only"],
        "tiktok": "screenshot_only",
        "notes": [
            "Apify STARTER plan limit exhausted after Cambly run.",
            "Meta Ad Library without auth: ~5-23 unique ads per search page (no pagination without login).",
            "AntiShkola query matched 'AntiSchool Online - английский онлайн' (Ukrainian brand) — closest Meta Ad Library match. Anti-shkola.ru (RU) may not have active Meta ads.",
            "Lindsay Does Languages confirmed no paid Meta ads — organic channel only."
        ]
    },
    "by_competitor": by_competitor,
    "landing_urls": sorted(all_landing_urls.values(), key=lambda x: -x["ad_count"]),
    "tiktok_top_ads": tiktok_top_ads,
}

out_path = f"{BASE}/data/creatives.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Written: {out_path}")
print(f"Total creatives: {total_creatives}")
for brand, v in by_competitor.items():
    note = f" [{v['note'][:60]}]" if 'note' in v else ''
    print(f"  {brand}: {v['total_ads']} ads | {v.get('active_ads',0)} active | {v.get('evergreen_ads',0)} evergreen{note}")
print(f"  Landing URLs: {len(all_landing_urls)}")
print("\nSample texts:")
for brand, v in by_competitor.items():
    ads = v.get('creatives', [])
    if ads:
        a = ads[0]
        print(f"  {brand}: [{a['start_date']}] {a['media_type']} | {a['text'][:100]}")
