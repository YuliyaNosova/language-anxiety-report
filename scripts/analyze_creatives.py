"""
Hook-Body-CTA-Offer analyzer для креативов конкурентов в нише "language anxiety".
Читает data/creatives.json, пишет data/analysis.json.

Логика: эвристический классификатор на основе текста объявления + page_name + media_type.
Все скоры — целые числа 1..10, overall_score = round(mean(hook,body,cta,offer), 1).
"""
import json
import re
import statistics
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "data" / "creatives.json"
OUT = ROOT / "data" / "analysis.json"

# ---------- лексиконы ----------
PAIN_LEX = {
    "fear":       ["боюс", "боюсь", "боятся", "страх", "не бойся", "afraid", "fear", "scared", "лякаєш", "соромно", "shy", "shame", "стыд", "стесн"],
    "stupor":     ["ступор", "freeze", "блок", "block", "молчу", "не могу сказать", "не можу сказати", "пугает диалог", "не нахожу слов", "stuck", "забываю слова"],
    "perfection": ["идеаль", "перфекц", "грамматик", "ошиб", "правильно говорить", "mistake", "perfect", "правил"],
    "shame":      ["стыд", "соромно", "стесняюсь", "embarrass", "ashamed", "позор"],
    "motivation": ["мотивац", "учу годами", "не получается", "не выучил", "no progress", "годами"],
    "result":     ["заговор", "fluent", "fluently", "confident", "уверенно", "результат", "B1", "B2", "C1", "level up", "новый уровень", "новий рівень"],
    "convenience":["удобно", "anywhere", "anytime", "когда угодно", "тариф", "price", "ціна", "розклад"],
}

HOOK_TYPES = ["problem", "result", "shock", "social_proof", "question", "trend"]
BODY_TYPES = ["before-after", "demo", "testimonial", "list", "story", "educational"]
CTA_TYPES = ["direct", "soft", "urgency", "free", "social"]
OFFER_TYPES = ["discount", "bundle", "trial", "free_shipping", "guarantee", "exclusive"]


def detect_pain_tags(text):
    t = text.lower()
    tags = []
    for tag, kws in PAIN_LEX.items():
        if any(kw in t for kw in kws):
            tags.append(tag)
    return tags or ["functional"]


def classify_hook(text):
    """Возвращает (type, hook_text, score, notes)."""
    t = text.strip()
    tl = t.lower()
    first_line = t.split("\n", 1)[0][:160]

    # Question
    if "?" in first_line and len(first_line) < 140:
        return ("question", first_line, 6, "Открывается вопросом, тянет любопытство")
    # Social proof — цифры, отзывы, "millions"
    if re.search(r"\b(\d{2,}[+kк]|million|миллион|тысяч|10\s?000|1m|users|студент|учеников|учнів|відгук|отзыв)", tl):
        return ("social_proof", first_line, 7, "Социальное доказательство через числа/отзывы")
    # Shock — emoji-bait, восклицания, "ИИ", "AI"
    if re.search(r"(🚀|🔥|wow|нарешті|finally|секрет|secret|hack|лайфхак)", tl):
        return ("shock", first_line, 6, "Эмоциональный/тизерный хук")
    # Problem — боль/страх/стыд
    pains = detect_pain_tags(text)
    if any(p in pains for p in ("fear", "stupor", "shame", "perfection", "motivation")):
        return ("problem", first_line, 7, f"Давит на боль: {','.join(pains)}")
    # Result — fluent / новый уровень / заговори
    if "result" in pains or re.search(r"(fluently|fluent|confident|заговор|новий рівень|новый уровень|level up)", tl):
        return ("result", first_line, 7, "Хук через обещание результата")
    # Trend — AI / ChatGPT
    if re.search(r"\b(ai|ии|chatgpt|gpt|нейросет)", tl):
        return ("trend", first_line, 6, "Привязка к AI-тренду")
    return ("result", first_line, 5, "Хук общий, без острой боли")


def classify_body(text, media_type):
    tl = text.lower()
    has_bullets = bool(re.search(r"[✔✅•\-—] ", text)) or text.count("✅") >= 2 or text.count("✔") >= 2
    has_testimonial = bool(re.search(r"[«\"](.*?)[»\"]", text)) and len(text) > 80
    has_story = bool(re.search(r"(я учил|я вчила|я не міг|years|годами|потом я|потім я|after|после того)", tl))
    has_before_after = bool(re.search(r"(было\s?[-—]\s?стало|до\s?[-—]\s?после|before.*after|с уровня|з рівня|за\s?\d+\s?(тиж|неде|месяц|month|week))", tl))
    has_edu = bool(re.search(r"(почему|why|правил|grammar|урок|разбор|tip)", tl))

    if has_before_after:
        return ("before-after", text[:220], 8, "Явная трансформация уровень/срок")
    if has_testimonial:
        return ("testimonial", text[:220], 7, "Цитата-отзыв в теле")
    if has_story:
        return ("story", text[:220], 7, "Нарратив 'я учил годами'")
    if has_bullets:
        return ("list", text[:220], 6, "Буллеты фич/выгод")
    if has_edu:
        return ("educational", text[:220], 6, "Обучающий разбор")
    if media_type == "video":
        return ("demo", text[:220], 6, "Видео-демо продукта")
    return ("list", text[:220], 5, "Тело-описание без яркой структуры")


def classify_cta(text):
    tl = text.lower()
    # Urgency
    if re.search(r"(только сегодня|останні місця|last chance|limited|спеши|до конца|залишилось)", tl):
        return ("urgency", "urgency phrase", 7, "Дедлайн/ограничение")
    # Free / trial
    if re.search(r"(free trial|free lesson|пробн|безкоштов|бесплат|14 days free|first lesson free|try free)", tl):
        return ("free", "free trial / free lesson", 7, "Free trial / бесплатный урок")
    # Social
    if re.search(r"(join|присоединяй|приєднуйся|millions|тысячи студентов)", tl):
        return ("social", "join community", 6, "Призыв через комьюнити")
    # Direct
    if re.search(r"(sign up|install now|download|регистрируйся|зареєструйся|записаться|записатися|купить|купити|start now|get started)", tl):
        return ("direct", "sign up / install / register", 7, "Прямой призыв к действию")
    # Soft
    if re.search(r"(learn more|узнай|дізнайся|подробнее|see how|читать|read more)", tl):
        return ("soft", "learn more", 5, "Мягкий CTA")
    return ("soft", "implicit cta", 4, "CTA размыт")


def classify_offer(text):
    tl = text.lower()
    # Discount
    if re.search(r"(\d{1,2}\s?%|скидк|знижк|sale|off|акция|акція)", tl):
        return ("discount", "discount %", 7, "Скидка")
    # Guarantee
    if re.search(r"(гарантія|гарантия|guarantee|вернем деньги|money-back|якщо не.*безкоштовно)", tl):
        return ("guarantee", "guarantee", 8, "Гарантия результата / возврата")
    # Trial
    if re.search(r"(free trial|14 days free|пробн|безкоштовн.*урок|trial)", tl):
        return ("trial", "free trial", 7, "Free trial")
    # Bundle / марафон
    if re.search(r"(марафон|курс|программа|програма|интенсив|інтенсив|bundle|pack)", tl):
        return ("bundle", "course/marathon bundle", 6, "Пакет/марафон/курс")
    # Exclusive
    if re.search(r"(эксклюзив|exclusive|vip|limited edition|спецпредложение)", tl):
        return ("exclusive", "exclusive access", 6, "Эксклюзивный доступ")
    return ("trial", "implicit trial", 4, "Оффер явно не сформулирован")


VISUAL_BY_MEDIA = {
    "video": "ugc",          # default допущение, заменяем для каталога
    "image": "product",
    "carousel": "product",
    "dynamic": "product",
}

EMOTION_BY_PAIN = {
    "fear": "fear",
    "shame": "fear",
    "stupor": "fear",
    "perfection": "fear",
    "motivation": "desire",
    "result": "desire",
    "convenience": "trust",
    "functional": "trust",
}


def analyze_one(c):
    text = c.get("text") or ""
    media = c.get("media_type") or "image"
    brand = c.get("brand", "?")
    page_name = c.get("page_name", "")

    # Catalog noise (Cambly dynamic templates)
    is_dynamic = "{{product" in text or "{{" in text

    hook = classify_hook(text if not is_dynamic else f"{brand} {page_name}")
    body = classify_body(text if not is_dynamic else page_name, media)
    cta = classify_cta(text)
    offer = classify_offer(text)
    pain_tags = detect_pain_tags(text)

    # Скидываем скоры у динамических каталожных
    if is_dynamic:
        hook = (hook[0], hook[1], 3, "Динамический каталожный шаблон, нет копирайта")
        body = (body[0], body[1], 3, "Шаблон каталога, не нарратив")
        cta = ("soft", "implicit", 3, "Нет явного CTA в шаблоне")
        offer = ("trial", "n/a", 3, "Шаблон, оффер не сформулирован")
        pain_tags = ["functional"]

    visual = VISUAL_BY_MEDIA.get(media, "product")
    if is_dynamic:
        visual = "product"
    emotion = EMOTION_BY_PAIN.get(pain_tags[0], "trust")

    scores = [hook[2], body[2], cta[2], offer[2]]
    overall = round(statistics.mean(scores), 1)

    # Сильный/слабый элемент
    elem_map = {"hook": hook[2], "body": body[2], "cta": cta[2], "offer": offer[2]}
    standout = max(elem_map, key=elem_map.get)
    weakness = min(elem_map, key=elem_map.get)

    # Целевой сегмент по бренду + языку
    target = {
        "TalkPal": "Self-learners A2-B2, ищут AI-разговор",
        "Speak":   "Self-learners A2-B1, мобильный AI-tutor",
        "Cambly":  "Adults 25-45, ищут native-tutor разговор",
        "AntiShkola": "Адульты СНГ/UA, A2-B2, марафоны",
        "Lindsay": "Self-learners, контент-driven",
    }.get(brand, "Adults A2-B2")

    return {
        "id": c.get("id"),
        "brand": brand,
        "text": text[:500],
        "hook":  {"type": hook[0],  "text": hook[1],  "score": hook[2],  "notes": hook[3]},
        "body":  {"type": body[0],  "text": body[1],  "score": body[2],  "notes": body[3]},
        "cta":   {"type": cta[0],   "text": cta[1],   "score": cta[2],   "notes": cta[3]},
        "offer": {"type": offer[0], "text": offer[1], "score": offer[2], "notes": offer[3]},
        "visual_style": visual,
        "emotional_trigger": emotion,
        "target_segment": target,
        "pain_tags": pain_tags,
        "is_dynamic_template": is_dynamic,
        "overall_score": overall,
        "standout_element": standout,
        "weakness": weakness,
    }


def main():
    data = json.loads(IN.read_text(encoding="utf-8"))
    by_c = data["by_competitor"]
    all_ads = []
    for brand, block in by_c.items():
        for c in block.get("creatives", []):
            all_ads.append(analyze_one(c))

    # Top 10 по overall_score
    top10 = sorted(all_ads, key=lambda x: x["overall_score"], reverse=True)[:10]

    # Распределение элементов
    def dist(field, options):
        d = {o: 0 for o in options}
        for a in all_ads:
            t = a[field]["type"]
            d[t] = d.get(t, 0) + 1
        return d

    element_distribution = {
        "hooks": dist("hook", HOOK_TYPES),
        "bodies": dist("body", BODY_TYPES),
        "ctas": dist("cta", CTA_TYPES),
        "offers": dist("offer", OFFER_TYPES),
    }

    # Pain distribution
    pain_counts = {}
    for a in all_ads:
        for p in a["pain_tags"]:
            pain_counts[p] = pain_counts.get(p, 0) + 1

    # Hook × Pain matrix (для гипотезы #2)
    hook_pain = {}
    for a in all_ads:
        h = a["hook"]["type"]
        for p in a["pain_tags"]:
            hook_pain.setdefault(h, {}).setdefault(p, 0)
            hook_pain[h][p] += 1

    # before/after по эмоциям — отдельная проверка
    emo_ba = 0
    level_ba = 0
    for a in all_ads:
        if a["body"]["type"] == "before-after":
            t = a["text"].lower()
            if any(x in t for x in ("страх", "стыд", "ступор", "уверен", "confident", "соромно", "блок", "уверенность")):
                emo_ba += 1
            if re.search(r"(a\d|b\d|c\d|уровень|рівень|level)", t):
                level_ba += 1

    out = {
        "analysis_date": str(date.today()),
        "total_analyzed": len(all_ads),
        "creatives": all_ads,
        "top_10_creatives": [a["id"] for a in top10],
        "element_distribution": element_distribution,
        "pain_distribution": pain_counts,
        "hook_x_pain_matrix": hook_pain,
        "hypothesis_2_check": {
            "before_after_total": sum(1 for a in all_ads if a["body"]["type"] == "before-after"),
            "before_after_emotional": emo_ba,
            "before_after_level_only": level_ba,
            "verdict": (
                "Подтверждена: эмоциональных before/after почти нет, доминирует уровневой"
                if emo_ba < level_ba else
                "Опровергнута: эмоциональных before/after не меньше уровневых"
            ),
        },
        "by_brand_avg_score": {
            b: round(statistics.mean([a["overall_score"] for a in all_ads if a["brand"] == b]), 2)
            for b in {a["brand"] for a in all_ads}
        },
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # Короткий вывод (только метаданные)
    print("WROTE:", OUT)
    print("total:", len(all_ads))
    print("hooks:", element_distribution["hooks"])
    print("bodies:", element_distribution["bodies"])
    print("ctas:", element_distribution["ctas"])
    print("offers:", element_distribution["offers"])
    print("pain:", pain_counts)
    print("hyp2:", out["hypothesis_2_check"])
    print("avg by brand:", out["by_brand_avg_score"])
    print("hook×pain:", json.dumps(hook_pain, ensure_ascii=False))


if __name__ == "__main__":
    main()
