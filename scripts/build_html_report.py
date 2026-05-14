#!/usr/bin/env python3
"""Build a self-contained HTML report from 6 JSON artefacts."""
import json
import os
from html import escape
from pathlib import Path

BASE = Path("/Users/yuliyanosova/vibecoding/research/language-anxiety")
DATA = BASE / "data"
OUT = BASE / "report.html"


def load(name):
    return json.load(open(DATA / name))


comp = load("competitors.json")
crea = load("creatives.json")
ana = load("analysis.json")
pat = load("patterns.json")
tra = load("traffic.json")
lan = load("landings.json")


def e(s):
    return escape(str(s)) if s is not None else ""


# ----- Builders for each section -----

CLUSTER_LABELS = {
    "direct": "Прямые конкуренты",
    "indirect": "Косвенные (нейросети / разговорные клубы)",
    "leaders": "Лидеры рынка",
    "emerging": "Растущие / нишевые",
}

CLUSTER_COLORS = {
    "direct": "#e11d48",
    "indirect": "#0ea5e9",
    "leaders": "#7c3aed",
    "emerging": "#f59e0b",
}


def cluster_for(name, clusters):
    for k, v in clusters.items():
        if isinstance(v, list) and name in v:
            return k
    return "indirect"


def section_hero():
    return f"""
<section id="hero" class="hero">
  <div class="hero-tag">КОНКУРЕНТНЫЙ АНАЛИЗ · {e(comp['analysis_date'])}</div>
  <h1>Языковой барьер: что делают конкуренты</h1>
  <p class="hero-sub">Снятие психологического блока в говорении на иностранном языке. Карта брендов, разбор рекламы, каналы трафика, посадочные страницы, проверка гипотез.</p>
  <div class="hero-stats">
    <div class="stat"><div class="stat-n">{e(comp['total_found'])}</div><div class="stat-l">брендов в карте</div></div>
    <div class="stat"><div class="stat-n">{e(crea['total_creatives'])}</div><div class="stat-l">рекламных объявлений</div></div>
    <div class="stat"><div class="stat-n">5</div><div class="stat-l">сайтов в глубоком разборе</div></div>
    <div class="stat accent"><div class="stat-n">3/3</div><div class="stat-l">гипотезы подтверждены</div></div>
  </div>
  <div class="hero-meta">
    <span>Россия + СНГ + русскоязычные за рубежом; сравнение — англоязычный рынок</span>
    <span>·</span>
    <span>3 000 — 30 000 ₽/мес (массовый сегмент); сравнение — 30–300 $/мес</span>
  </div>
</section>
"""


def section_about():
    return """
<section id="about">
  <h2>О чём это исследование</h2>

  <h3>Какую боль анализируем</h3>
  <p><strong>Языковой барьер в разговорной речи</strong> — психологическое состояние, при котором человек понимает иностранный язык, читает на нём, но в живом разговоре «застывает». В академической литературе это называют <em>Foreign Language Anxiety</em> (далее в отчёте — языковой барьер). Симптомы устойчивые и распознаваемые:</p>
  <ul>
    <li>«Всё понимаю — сказать не могу»</li>
    <li>Страх допустить ошибку, страх осуждения собеседника</li>
    <li>Ступор перед звонком, переговорами, разговором с носителем</li>
    <li>Перфекционизм: «сначала выучу всё — потом заговорю» — годами</li>
    <li>Физическая реакция: учащённое сердцебиение, потеют ладони, голос пропадает</li>
  </ul>

  <h3>Кто целевая аудитория</h3>
  <div class="grid-2">
    <div class="card">
      <h4>Портрет клиента</h4>
      <ul>
        <li>Русскоязычные взрослые, 25–45 лет</li>
        <li>Уровень изучаемого языка — A2–B2 (от «могу читать с словарём» до «понимаю фильмы, но молчу»)</li>
        <li>Учат не первый год, часто 3–10 лет. Фрустрированы отсутствием результата именно в говорении</li>
        <li>География: Россия, СНГ, русскоязычные за рубежом (релоканты, мигранты, репатрианты)</li>
        <li>Готовы платить 3 000 – 30 000 ₽/мес за решение боли</li>
      </ul>
    </div>
    <div class="card">
      <h4>Что для них важно</h4>
      <ul>
        <li>Снять психологический блок — не выучить ещё одну тему грамматики</li>
        <li>Безопасная среда практики без оценок</li>
        <li>Не «уроки», а «разговоры»</li>
        <li>Эмоциональное «до и после» — а не «уровень B1 за 3 месяца»</li>
        <li>Доверие к эксперту, который сам прошёл этот путь</li>
      </ul>
    </div>
  </div>

  <h3>Кого считаем конкурентом</h3>
  <div class="grid-2">
    <div class="card">
      <h4>Включаем в анализ</h4>
      <ul>
        <li>Тех, кто прямо адресует <strong>проблему блока в говорении</strong>, а не «выучи язык за 3 месяца»</li>
        <li>Приложения с нейросетью для разговорной практики (TalkPal, Speak и аналоги)</li>
        <li>Разговорные клубы без оценок</li>
        <li>Платформы с носителями (Cambly, italki) — как образец для каналов и копирайтинга</li>
        <li>Психологов-наставников, работающих со страхом речи (Машкова, Кашпур)</li>
        <li>Англоязычных эксперт-блогеров: Lindsay Williams, Olly Richards — как образец воронки и контента</li>
      </ul>
    </div>
    <div class="card">
      <h4>НЕ включаем</h4>
      <ul>
        <li>Массовые языковые школы общего профиля (Skyeng, EnglishDom, Tutor.com) — их продукт про грамматику и уровень, не про блок</li>
        <li>Языковые приложения для самообучения (Duolingo, Babbel) — не работают с речью и страхом</li>
        <li>Подготовку к экзаменам (IELTS, TOEFL) — другая боль, другая аудитория</li>
      </ul>
    </div>
  </div>

  <h3>По каким критериям отбирали топ-5</h3>
  <p>Из 20 брендов на карте в глубокий разбор взяли пять, набравших баллы по четырём осям:</p>
  <ol>
    <li><strong>Соответствие нише</strong> — насколько прямо адресует языковой барьер, а не учит грамматике</li>
    <li><strong>Маркетинговая активность</strong> — наличие живой рекламы в Meta Ad Library / TikTok Creative Center и видимое присутствие в каналах</li>
    <li><strong>Релевантность аудитории</strong> — русскоязычный сегмент или прямая модель для повторения (англоязычный образец)</li>
    <li><strong>Полнота воронки</strong> — есть посадочная страница, понятная цена, реклама, контент-каналы</li>
  </ol>

  <h3>Как анализировали — методология в 7 шагах</h3>
  <div class="method-steps">
    <div class="method-step"><span class="ms-num">1</span><div><strong>Карта конкурентов.</strong> Сканирование рынка через Exa-поиск: 20 брендов в 4 группах (прямые, косвенные, лидеры рынка, растущие нишевые). Сверка с обязательным cross-check-списком из брифа.</div></div>
    <div class="method-step"><span class="ms-num">2</span><div><strong>Сбор рекламы.</strong> Все активные и завершённые объявления топ-5 за последние 90 дней из библиотеки рекламы Meta (через Apify) и TikTok Creative Center. Итог — 105 объявлений с полным текстом, датами, форматами, регионами.</div></div>
    <div class="method-step"><span class="ms-num">3</span><div><strong>Разбор каждого объявления.</strong> Каждое из 105 разложено на четыре элемента: <em>заход</em> (первая строка, что цепляет), <em>раскрытие</em> (тело сообщения), <em>призыв</em> (CTA), <em>предложение</em> (оффер). Размечено по типам боли клиента: страх / стыд / ступор / перфекционизм / мотивация / результат / удобство / функционал. Каждому объявлению проставлен скор 1–10.</div></div>
    <div class="method-step"><span class="ms-num">4</span><div><strong>Поиск закономерностей.</strong> Кросс-брендовые повторяющиеся приёмы, A/B-тесты внутри одного бренда, evergreen-победители (то, что бренд крутит 30+ дней). Построена матрица «заход × боль» для поиска пустых ниш. Сгенерировано 10 идей объявлений в свободные ниши.</div></div>
    <div class="method-step"><span class="ms-num">5</span><div><strong>Каналы трафика.</strong> Для каждого из топ-5 — распределение по источникам (платный, органика, прямой, реферальный), оценка месячного бюджета на рекламу, ключевые гео, видимость в России и СНГ, активные соцсети.</div></div>
    <div class="method-step"><span class="ms-num">6</span><div><strong>Посадочные страницы.</strong> Разбор главной страницы каждого из топ-5: первый экран, структура секций, тип социальных доказательств, оффер и цены, формы заявки. Проверка гипотезы №3 — какие отзывы дают конкуренты.</div></div>
    <div class="method-step"><span class="ms-num">7</span><div><strong>Финальный отчёт.</strong> Сборка выводов, проверка трёх гипотез из брифа, план приоритетных тестов.</div></div>
  </div>

  <div class="callout warn">
    <div class="callout-label">Что важно помнить при чтении отчёта</div>
    <p>Все цифры по трафику и рекламным бюджетам — оценочные (SimilarWeb, Semrush, Ahrefs закрыты платной подпиской). Объём рекламы в библиотеке Meta без авторизации ограничен (5–23 объявления на бренд). Полностью удалось выгрузить только Cambly через сервис Apify. Lindsay Does Languages платную рекламу не ведёт — анализировали только посадочную страницу и органические каналы.</p>
  </div>
</section>
"""


def section_summary():
    insight = comp.get("market_insights", "")
    opp_list = tra.get("opportunities", [])[:3]
    opp_html = ""
    for o in opp_list:
        if isinstance(o, dict):
            title = o.get("opportunity") or o.get("name") or o.get("title") or ""
            desc = o.get("rationale") or o.get("description") or o.get("why") or ""
            opp_html += f'<li><strong>{e(title)}</strong> — {e(desc)}</li>'
        else:
            opp_html += f"<li>{e(o)}</li>"
    return f"""
<section id="summary">
  <h2>1. Главные выводы</h2>
  <div class="callout key">
    <div class="callout-label">Главная находка</div>
    <p>{e(insight)}</p>
  </div>
  <div class="grid-2">
    <div class="card">
      <h3>Что делают конкуренты</h3>
      <ul>
        <li><strong>Приложения с нейросетью</strong> (TalkPal, Speak, Loora) — массовый продукт, но без работы со страхом</li>
        <li><strong>Психологи-наставники</strong> (Машкова, Кашпур) — работа с эмоциями, но малые потоки клиентов</li>
        <li><strong>Языковые школы</strong> — методика грамматики, психологический блок игнорируют</li>
        <li><strong>Площадки с носителями</strong> (Cambly, italki) — практика речи, но без разбора страха</li>
      </ul>
    </div>
    <div class="card">
      <h3>Рыночные возможности</h3>
      <ol>{opp_html}</ol>
    </div>
  </div>
</section>
"""


def section_competitors():
    rows = ""
    for c in comp["competitors"]:
        cl = c.get("cluster", "indirect")
        color = CLUSTER_COLORS.get(cl, "#888")
        rows += f"""
<tr>
  <td><strong>{e(c['name'])}</strong><br><a href="{e(c.get('url',''))}" target="_blank" class="muted">{e(c.get('url',''))}</a></td>
  <td><span class="tag" style="background:{color}">{e(CLUSTER_LABELS.get(cl, cl))}</span></td>
  <td>{e(c.get('positioning',''))}</td>
  <td>{e(c.get('ad_presence','—'))}</td>
</tr>
"""

    top5_html = ""
    for i, t in enumerate(comp["top_5"], 1):
        top5_html += f"""
<div class="top-card">
  <div class="top-rank">{i}</div>
  <div class="top-body">
    <h4>{e(t['name'])} <a href="{e(t['url'])}" target="_blank" class="muted small">↗</a></h4>
    <p>{e(t['reason'])}</p>
  </div>
</div>
"""

    cc = comp.get("cross_check_status", {})
    cc_status = "passed" if cc.get("cross_check_passed") else "warn"
    cc_text = cc.get("note", "")

    return f"""
<section id="competitors">
  <h2>2. Карта конкурентов</h2>

  <h3>Топ-5 для глубокого разбора</h3>
  <div class="top-grid">{top5_html}</div>

  <div class="callout {cc_status}">
    <div class="callout-label">Сверка по списку из брифа</div>
    <p>{e(cc_text)}</p>
  </div>

  <h3>Полная карта — 20 брендов</h3>
  <table class="data-table">
    <thead><tr><th>Бренд</th><th>Группа</th><th>Позиционирование</th><th>Активность рекламы</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>
"""


def section_creatives():
    fa = pat["frequency_analysis"]
    missing = fa.get("missing_patterns", [])
    miss_html = "".join(f'<li><code>{e(m)}</code></li>' for m in missing)

    # Hook×pain matrix
    hxp = ana["hook_x_pain_matrix"]
    pain_keys = set()
    for hook, pains in hxp.items():
        if isinstance(pains, dict):
            pain_keys.update(pains.keys())
    pain_keys = sorted(pain_keys)
    matrix_rows = ""
    for hook, pains in hxp.items():
        cells = ""
        if isinstance(pains, dict):
            for pk in pain_keys:
                v = pains.get(pk, 0)
                intensity = min(255, int(v * 8))
                bg = f"rgba(225, 29, 72, {min(0.85, v/30):.2f})" if v else "transparent"
                fg = "#fff" if v > 15 else "#1a1a1a"
                cells += f'<td style="background:{bg};color:{fg}">{v}</td>'
        matrix_rows += f'<tr><th>{e(hook)}</th>{cells}</tr>'
    matrix_head = "".join(f'<th>{e(p)}</th>' for p in pain_keys)

    avg = ana["by_brand_avg_score"]
    brand_rows = ""
    for b, sc in sorted(avg.items(), key=lambda x: -x[1]):
        bar_w = int((sc / 10) * 100)
        brand_rows += f"""
<div class="bar-row">
  <div class="bar-name">{e(b)}</div>
  <div class="bar"><div class="bar-fill" style="width:{bar_w}%"></div></div>
  <div class="bar-val">{sc}</div>
</div>
"""

    # Top hooks
    top_hooks = fa.get("top_hooks", [])
    hook_html = ""
    for h in top_hooks[:5]:
        if isinstance(h, dict):
            hook_html += f'<li><strong>{e(h.get("hook","?"))}</strong> — {e(h.get("count","?"))} креативов <span class="muted">({e(h.get("share",""))})</span></li>'

    return f"""
<section id="creatives">
  <h2>3. Разбор рекламы — 105 объявлений</h2>

  <div class="grid-2">
    <div class="card">
      <h3>Средняя оценка качества рекламы</h3>
      {brand_rows}
    </div>
    <div class="card">
      <h3>Самые частые заходы у конкурентов</h3>
      <ul>{hook_html}</ul>
    </div>
  </div>

  <h3>Заход × боль — где сосредоточены конкуренты</h3>
  <p class="muted">Чем темнее ячейка, тем больше объявлений в этом сочетании захода и боли клиента. Пустые столбцы — свободные ниши.</p>
  <table class="matrix">
    <thead><tr><th>Заход \\ Боль</th>{matrix_head}</tr></thead>
    <tbody>{matrix_rows}</tbody>
  </table>

  <div class="callout danger">
    <div class="callout-label">Полностью свободные ниши (0 из 105 объявлений)</div>
    <ul class="pill-list">{miss_html}</ul>
  </div>
</section>
"""


def section_ideas():
    cards = ""
    type_color = {"safe": "#10b981", "wild": "#a855f7", "balanced": "#f59e0b"}
    type_label = {"safe": "безопасно", "wild": "смело", "balanced": "сбалансировано"}
    prio_color = {"P0": "#e11d48", "P1": "#f59e0b", "P2": "#64748b"}
    prio_label = {"P0": "первая очередь", "P1": "вторая очередь", "P2": "третья очередь"}
    for idea in pat["creative_ideas"]:
        t = idea.get("type", "")
        p = idea.get("priority", "")
        tcolor = type_color.get(t, "#64748b")
        pcolor = prio_color.get(p, "#64748b")
        cards += f"""
<div class="idea-card">
  <div class="idea-head">
    <div class="idea-id">#{e(idea.get('id',''))}</div>
    <div class="idea-tags">
      <span class="tag" style="background:{pcolor}">{e(prio_label.get(p, p))}</span>
      <span class="tag" style="background:{tcolor}">{e(type_label.get(t, t))}</span>
    </div>
  </div>
  <h4>{e(idea.get('title',''))}</h4>
  <div class="idea-line"><span class="lbl">Заход</span><span>{e(idea.get('hook',''))}</span></div>
  <div class="idea-line"><span class="lbl">Раскрытие</span><span>{e(idea.get('body',''))}</span></div>
  <div class="idea-line"><span class="lbl">Призыв</span><span>{e(idea.get('cta',''))}</span></div>
  <div class="idea-line"><span class="lbl">Предложение</span><span>{e(idea.get('offer',''))}</span></div>
  <div class="idea-line"><span class="lbl">Картинка</span><span>{e(idea.get('visual_concept',''))}</span></div>
  <div class="idea-foot">
    <span class="muted">{e(idea.get('target_segment',''))}</span>
  </div>
</div>
"""
    return f"""
<section id="ideas">
  <h2>4. Десять идей для рекламы</h2>
  <p class="muted">Каждая идея бьёт в одну из найденных свободных ниш: заход через боль клиента, эмоциональное «до и после», личная история, дефицит времени или мест, противопоставление приложениям с нейросетью.</p>
  <div class="ideas-grid">{cards}</div>
</section>
"""


def section_traffic():
    rows = ""
    for c in tra["competitors"]:
        mv = c.get("monthly_visits") or c.get("monthly_visits_estimate") or "—"
        pv = c.get("paid_vs_organic", {})
        pv_str = f'платный {pv.get("paid","?")} / органика {pv.get("organic","?")}' if isinstance(pv, dict) else "—"
        rus = c.get("ru_cis_presence", "—")
        spend = c.get("estimated_ad_spend", "—")
        rows += f"""
<tr>
  <td><strong>{e(c['name'])}</strong></td>
  <td>{e(mv)}</td>
  <td>{e(pv_str)}</td>
  <td>{e(rus)}</td>
  <td>{e(spend)}</td>
</tr>
"""

    opps = tra.get("opportunities", [])
    opp_html = ""
    for o in opps:
        if isinstance(o, dict):
            title = o.get("opportunity") or o.get("name") or o.get("title") or ""
            desc = o.get("rationale") or o.get("description") or o.get("why") or ""
            opp_html += f"<li><strong>{e(title)}</strong> — {e(desc)}</li>"
        else:
            opp_html += f"<li>{e(o)}</li>"

    return f"""
<section id="traffic">
  <h2>5. Каналы продвижения у топ-5</h2>
  <table class="data-table">
    <thead><tr><th>Бренд</th><th>Посещений в месяц</th><th>Платный / органический трафик</th><th>Присутствие в РФ/СНГ</th><th>Оценка бюджета рекламы</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="callout warn">
    <div class="callout-label">Замечание о данных</div>
    <p>{e(tra.get('data_availability_note',''))}</p>
  </div>
  <h3>Свободные канальные возможности</h3>
  <ol class="big-list">{opp_html}</ol>
</section>
"""


def section_landings():
    cards = ""
    for l in lan["landings"]:
        score = l.get("overall_score", "?")
        atf = l.get("above_the_fold", {})
        head = atf.get("headline", "") if isinstance(atf, dict) else ""
        sub = atf.get("subheadline", "") if isinstance(atf, dict) else ""
        cta = atf.get("cta_text", "") if isinstance(atf, dict) else ""

        s_html = "".join(f"<li>{e(s)}</li>" for s in (l.get("strengths") or [])[:5])
        w_html = "".join(f"<li>{e(s)}</li>" for s in (l.get("weaknesses") or [])[:5])

        cards += f"""
<div class="landing-card">
  <div class="landing-head">
    <div>
      <h4>{e(l['brand'])}</h4>
      <a href="{e(l.get('url',''))}" target="_blank" class="muted small">{e(l.get('url',''))}</a>
    </div>
    <div class="score-circle"><div class="score-n">{e(score)}</div><div class="score-l">/10</div></div>
  </div>
  <div class="landing-hero">
    <div class="lh-label">ПЕРВЫЙ ЭКРАН</div>
    <p class="lh-headline">«{e(head)}»</p>
    <p class="lh-sub">{e(sub)}</p>
    <p class="lh-cta">Кнопка: <strong>{e(cta)}</strong></p>
  </div>
  <div class="landing-grid">
    <div><h5>+ Сильные стороны</h5><ul>{s_html}</ul></div>
    <div><h5>− Слабые места</h5><ul>{w_html}</ul></div>
  </div>
</div>
"""

    insights_html = "".join(f"<li>{e(i)}</li>" for i in lan.get("cross_landing_insights", []))

    impact_color = {"high": "#e11d48", "medium": "#f59e0b", "low": "#64748b"}
    effort_color = {"low": "#10b981", "medium": "#f59e0b", "high": "#e11d48"}
    level_label = {"high": "высокий", "medium": "средний", "low": "низкий"}

    ideas_html = ""
    for i, idea in enumerate(lan["improvement_ideas"], 1):
        impact_raw = str(idea.get("expected_impact", "")).lower()
        effort_raw = str(idea.get("effort", "")).lower()
        ic = impact_color.get(impact_raw, "#64748b")
        ec = effort_color.get(effort_raw, "#64748b")
        impact_ru = level_label.get(impact_raw, impact_raw)
        effort_ru = level_label.get(effort_raw, effort_raw)
        ideas_html += f"""
<div class="lidea-card">
  <div class="lidea-rank">{i}</div>
  <div class="lidea-body">
    <h4>{e(idea.get('idea',''))}</h4>
    <p class="muted">Основа: {e(idea.get('based_on',''))}</p>
    <div class="lidea-tags">
      <span class="tag" style="background:{ic}">эффект: {e(impact_ru)}</span>
      <span class="tag" style="background:{ec}">трудозатраты: {e(effort_ru)}</span>
    </div>
  </div>
</div>
"""

    return f"""
<section id="landings">
  <h2>6. Разбор посадочных страниц топ-5</h2>
  <div class="landings-grid">{cards}</div>

  <h3>Сквозные наблюдения по всем пяти страницам</h3>
  <ol class="big-list">{insights_html}</ol>

  <h3>5 идей для улучшения собственной посадочной страницы</h3>
  <div class="lideas-grid">{ideas_html}</div>
</section>
"""


def section_hypotheses():
    h2 = ana["hypothesis_2_check"]
    h3 = lan["hypothesis_3_check"]
    return f"""
<section id="hypotheses">
  <h2>7. Проверка гипотез брифа</h2>

  <div class="hyp">
    <div class="hyp-num">№1</div>
    <div class="hyp-body">
      <h3>На русскоязычном рынке нет связки «методика + работа со страхом речи»</h3>
      <div class="verdict pass">ПОДТВЕРЖДЕНА</div>
      <p>Рынок поделён надвое: приложения с нейросетью (массовость без работы со страхом) и психологи-наставники (работа с эмоциями, но узкий поток клиентов). Anti-Shkola ближе всех к гибриду, но явной психологической методики не показывает.</p>
    </div>
  </div>

  <div class="hyp">
    <div class="hyp-num">№2</div>
    <div class="hyp-body">
      <h3>Реклама давит на «страх» и «стыд», но почти никто не показывает «до и после» по эмоциям</h3>
      <div class="verdict pass">ПОДТВЕРЖДЕНА В КРАЙНЕЙ ФОРМЕ</div>
      <div class="hyp-stats">
        <div><strong>{e(h2.get('before_after_emotional', 0))}</strong> из 105 — «до и после» по эмоциям</div>
        <div><strong>{e(h2.get('before_after_level_only', 0))}</strong> из 105 — «до и после» только по уровню языка</div>
      </div>
      <p>{e(h2.get('verdict',''))}</p>
    </div>
  </div>

  <div class="hyp">
    <div class="hyp-num">№3</div>
    <div class="hyp-body">
      <h3>Посадочные страницы перегружены методикой и недодают историй именно о снятии блока</h3>
      <div class="verdict pass">ПОДТВЕРЖДЕНА</div>
      <p>{e(h3)}</p>
    </div>
  </div>
</section>
"""


def section_tests():
    rows = ""
    prio_label = {"P0": "первая очередь", "P1": "вторая очередь", "P2": "третья очередь"}
    for t in pat["test_plan"]:
        p = t.get("priority", "")
        color = '#e11d48' if p == 'P0' else '#f59e0b' if p == 'P1' else '#64748b'
        rows += f"""
<div class="test-card">
  <div class="test-head">
    <span class="tag" style="background:{color}">{e(prio_label.get(p, p))}</span>
    <h4>{e(t.get('test_name',''))}</h4>
  </div>
  <p><strong>Гипотеза:</strong> {e(t.get('hypothesis',''))}</p>
  <p><strong>Что считаем успехом:</strong> {e(t.get('success_metric',''))}</p>
  <p class="muted"><strong>Бюджет:</strong> {e(t.get('budget_recommendation',''))}</p>
</div>
"""
    return f"""
<section id="tests">
  <h2>8. План тестов — что запускать в первую очередь</h2>
  <div class="tests-grid">{rows}</div>
</section>
"""


EMIGRANT_DATA = [
    {"country": "Германия", "lang": "немецкий", "brand": "Berliner Deutsch", "url": "https://berlinerdeutsch.ru",
     "format": "Разговорные клубы Zoom, до 42 встреч/нед на A1, группы 3-6 чел",
     "price": "от 6 €/встреча, ~25-40 €/мес", "channel": "Сайт + поиск Google",
     "note": "Низкий порог входа, ежедневная частота — снимает страх через регулярное воздействие"},
    {"country": "Германия", "lang": "немецкий", "brand": "Brandt Schule", "url": "https://t.me/brandtschule",
     "format": "Разговорные клубы, премиум-позиционирование «немецкий с удовольствием»",
     "price": "70 €/мес", "channel": "Только Telegram-канал",
     "note": "Прямо адресует «понимаю — не говорю», работает изнутри Telegram-сообществ релокантов"},
    {"country": "Израиль", "lang": "иврит", "brand": "Сабабушка", "url": "https://sababushka.com/club",
     "format": "4 или 8 разговорных клубов Zoom в неделю по 1.5 ч + словари и упражнения после каждой встречи",
     "price": "180-280 шек/мес (≈50-85 €)", "channel": "Telegram-сообщество",
     "note": "Самая зрелая модель сообщества и материалов — сочетает речь, когнитивную обработку и социальную поддержку"},
    {"country": "Израиль", "lang": "иврит", "brand": "Yad L'Olim", "url": "https://www.yadlolim.org/hebrew-conversation-club",
     "format": "Hebrew Conversation Club в 3 городах + онлайн, «non-judgemental environment with Olim like you»",
     "price": "бесплатно", "channel": "NGO + сарафанное радио",
     "note": "Прямо называет страх осуждения; используется как воронка в платные программы партнёров"},
    {"country": "Израиль", "lang": "иврит", "brand": "Арье Миретский", "url": "https://www.youtube.com/@ivrit.tiktok",
     "format": "Иврит через разбор израильских TikTok-роликов — живой сленг и культурный контекст",
     "price": "индивидуально", "channel": "YouTube",
     "note": "Уникальный подход — аутентичный контент вместо учебника"},
    {"country": "Сербия", "lang": "сербский", "brand": "Centar Slovo", "url": "https://www.centarslovo.rs",
     "format": "Аккредитованная школа A1-C2 в Белграде и онлайн, для ВНЖ",
     "price": "от 80 €/мес за группу", "channel": "Сайт + офлайн в Белграде",
     "note": "Единственный аккредитованный игрок в сегменте — даёт юридическую ценность для статуса ВНЖ"},
    {"country": "Сербия", "lang": "сербский", "brand": "EasyPass", "url": "https://easypass.mk",
     "format": "Онлайн-курсы сербского с прямым посылом «преодоление языкового барьера для русскоговорящих»",
     "price": "по запросу", "channel": "Сайт + соцсети",
     "note": "Самое точное по копирайту попадание в боль — но микробизнес"},
    {"country": "Любая", "lang": "15 языков", "brand": "Ковчег", "url": "https://kovcheg.live",
     "format": "Благотворительные курсы языков для русскоязычных эмигрантов с антивоенной позицией",
     "price": "бесплатно", "channel": "Сообщество эмигрантов",
     "note": "1500+ учеников, 15 языков, волонтёры. Лучшая входная точка для эмигрантов — конкурент по вниманию, не по цене"},
]

EMIGRANT_GAPS = [
    "<strong>Польский</strong> для русскоязычных в Польше — есть только школы общего профиля (VARIA, GLOSSA), без специализации на боли релокантов",
    "<strong>Английский</strong> в Великобритании и Ирландии для русскоязычных — пусто, только государственные ESOL-курсы и Meetup-клубы",
    "<strong>Греческий</strong> на Кипре, <strong>португальский</strong> в Португалии, <strong>испанский</strong> в Испании — русскоязычных нишевых коучей по сути нет",
    "<strong>Грузинский, армянский</strong> — только государственные программы для этнической диаспоры, не для новой волны эмигрантов",
]


def section_emigrants():
    rows = ""
    for r in EMIGRANT_DATA:
        rows += f"""
<tr>
  <td><strong>{e(r['country'])}</strong><br><span class="muted small">{e(r['lang'])}</span></td>
  <td><strong>{e(r['brand'])}</strong><br><a href="{e(r['url'])}" target="_blank" class="muted small">{e(r['url'])}</a></td>
  <td>{e(r['format'])}</td>
  <td>{e(r['price'])}</td>
  <td>{e(r['channel'])}</td>
  <td class="muted">{e(r['note'])}</td>
</tr>
"""
    gaps_html = "".join(f"<li>{g}</li>" for g in EMIGRANT_GAPS)

    return f"""
<section id="emigrants">
  <h2>9. Русскоязычные эмигранты в Европе и Израиле</h2>
  <p class="muted">Отдельный пласт конкурентов, который не попал в основную карту: локальные коучи и микро-школы, обслуживающие волну релокации 2022+. Работают не как глобальные сервисы, а как сообщества внутри Telegram-чатов эмигрантов конкретной страны.</p>

  <div class="callout key">
    <div class="callout-label">Главный вывод</div>
    <p>Сегмент <strong>существует и активно растёт</strong>, но фрагментирован: микробренды одного человека, по 1-2 на страну. Боль <em>«понимаю, не говорю»</em> называют, но методически работают как обычные разговорные клубы или индивидуальные репетиторы. <strong>Психологической методики снятия блока не показывает никто</strong> — даже в этом сегменте.</p>
  </div>

  <h3>Конкретные игроки по странам</h3>
  <table class="data-table">
    <thead><tr><th>Страна / язык</th><th>Бренд</th><th>Формат</th><th>Цена</th><th>Главный канал</th><th>Что особенного</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>

  <div class="grid-2">
    <div class="card">
      <h3>Что выделяет успешных</h3>
      <ul>
        <li>Telegram как первичный канал, не сайт</li>
        <li>Малые группы 3-6 человек, гибкий график без обязательств</li>
        <li>Прямое называние боли в позиционировании</li>
        <li>Сочетание клуба + материалов + сообщества</li>
        <li>Доступные цены (от бесплатного до 85 €/мес) — поправка на экономическую уязвимость после переезда</li>
      </ul>
    </div>
    <div class="card">
      <h3>Свободные ниши</h3>
      <ol class="big-list">{gaps_html}</ol>
    </div>
  </div>

  <div class="callout key">
    <div class="callout-label">Стратегический вывод для продукта</div>
    <p>Если методика работает <strong>с языковым барьером независимо от языка</strong>, открывается уникальное позиционирование: <em>«работаю со страхом речи, а не с конкретным языком — неважно немецкий у тебя или иврит»</em>. Никто из 8 найденных брендов так не позиционируется — все привязаны к одному языку и одной стране. Telegram-каналы релокантских сообществ — главный вход в этот сегмент.</p>
  </div>
</section>
"""


def section_meta():
    return f"""
<section id="meta">
  <h2>10. Источники и оговорки</h2>
  <div class="grid-2">
    <div class="card">
      <h3>Файлы исследования</h3>
      <ul class="mono">
        <li><code>data/competitors.json</code> — 20 брендов в 4 группах</li>
        <li><code>data/creatives.json</code> — 105 объявлений из библиотеки рекламы Meta</li>
        <li><code>data/analysis.json</code> — заход / раскрытие / призыв / предложение × 105</li>
        <li><code>data/patterns.json</code> — 5 закономерностей + 10 идей</li>
        <li><code>data/traffic.json</code> — каналы трафика топ-5</li>
        <li><code>data/landings.json</code> — 5 посадочных страниц + 5 идей</li>
      </ul>
    </div>
    <div class="card">
      <h3>Ограничения данных</h3>
      <ul>
        <li><strong>Библиотека рекламы Meta</strong> без авторизации отдаёт около 5–23 объявлений на бренд. Полностью удалось выгрузить только Cambly (71 объявление) через сервис Apify.</li>
        <li><strong>SimilarWeb, Semrush, Ahrefs</strong> закрыты платной подпиской и защитой от парсинга. Цифры по трафику и бюджетам — оценочные.</li>
        <li><strong>Lindsay Does Languages</strong> — платной рекламы нет, разбирали только посадочную страницу и органические каналы.</li>
        <li><strong>Машкова и Кашпур</strong> через поиск как самостоятельные продукты не нашлись — только в виде репетиторов на агрегаторах.</li>
      </ul>
    </div>
  </div>
  <p class="muted small">Сборка отчёта: 7 шагов, 7 субагентов. Дата исследования — {e(comp['analysis_date'])}.</p>
</section>
"""


# ----- CSS -----
CSS = """
:root {
  --bg: #fafaf9;
  --surface: #ffffff;
  --text: #1a1a1a;
  --muted: #6b7280;
  --border: #e5e5e5;
  --accent: #e11d48;
  --accent-soft: #fce7ec;
  --green: #10b981;
  --amber: #f59e0b;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
}
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  max-width: 1400px;
  margin: 0 auto;
}
nav.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 32px 24px;
  border-right: 1px solid var(--border);
  overflow-y: auto;
  background: var(--surface);
}
nav.sidebar .brand {
  font-weight: 700;
  font-size: 14px;
  color: var(--accent);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 24px;
}
nav.sidebar ol { list-style: none; padding: 0; margin: 0; counter-reset: nav; }
nav.sidebar li { counter-increment: nav; margin: 0; }
nav.sidebar a {
  display: block;
  padding: 8px 0 8px 28px;
  color: var(--muted);
  text-decoration: none;
  font-size: 14px;
  position: relative;
  border-left: 2px solid transparent;
  transition: all 0.15s;
}
nav.sidebar a:before {
  content: counter(nav);
  position: absolute;
  left: 8px;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  color: var(--muted);
}
nav.sidebar a:hover { color: var(--text); }
nav.sidebar a.active { color: var(--accent); border-left-color: var(--accent); }
main { padding: 56px 64px; max-width: 980px; }
@media (max-width: 1000px) {
  .layout { grid-template-columns: 1fr; }
  nav.sidebar { position: relative; height: auto; border-right: 0; border-bottom: 1px solid var(--border); }
  main { padding: 32px 24px; }
}
section { margin: 0 0 96px; scroll-margin-top: 24px; }
section:last-child { margin-bottom: 0; }
h1 { font-size: 56px; font-weight: 800; line-height: 1.05; margin: 0 0 24px; letter-spacing: -0.02em; }
h2 { font-size: 32px; font-weight: 700; margin: 0 0 24px; letter-spacing: -0.01em; border-bottom: 2px solid var(--text); padding-bottom: 12px; }
h3 { font-size: 20px; font-weight: 600; margin: 40px 0 16px; }
h4 { font-size: 17px; font-weight: 600; margin: 0 0 8px; }
h5 { font-size: 14px; font-weight: 600; margin: 0 0 8px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
p { margin: 0 0 14px; }
a { color: var(--accent); }
.muted { color: var(--muted); }
.small { font-size: 13px; }
.mono { font-family: "SF Mono", Menlo, monospace; font-size: 13px; }
code { background: #f3f4f6; padding: 2px 6px; border-radius: 3px; font-family: "SF Mono", Menlo, monospace; font-size: 0.9em; }

/* Hero */
.hero { margin-bottom: 72px; }
.hero-tag { font-size: 12px; font-weight: 700; letter-spacing: 0.15em; color: var(--accent); margin-bottom: 16px; }
.hero-sub { font-size: 18px; color: var(--muted); max-width: 700px; margin-bottom: 36px; }
.hero-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 36px 0 24px; }
.stat { padding: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
.stat.accent { background: var(--accent); color: white; border-color: var(--accent); }
.stat-n { font-size: 36px; font-weight: 800; line-height: 1; margin-bottom: 8px; letter-spacing: -0.02em; }
.stat-l { font-size: 13px; opacity: 0.7; }
.hero-meta { display: flex; gap: 12px; font-size: 14px; color: var(--muted); }

/* Cards */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 24px; }
.card h3 { margin-top: 0; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 720px) { .grid-2 { grid-template-columns: 1fr; } .hero-stats { grid-template-columns: repeat(2, 1fr); } }

/* Callouts */
.callout { padding: 16px 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid; }
.callout-label { font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.callout p { margin: 0; }
.callout.key { background: var(--accent-soft); border-left-color: var(--accent); }
.callout.key .callout-label { color: var(--accent); }
.callout.warn { background: #fef3c7; border-left-color: var(--amber); }
.callout.warn .callout-label { color: var(--amber); }
.callout.passed, .callout.pass { background: #d1fae5; border-left-color: var(--green); }
.callout.passed .callout-label { color: var(--green); }
.callout.danger { background: #fef2f2; border-left-color: var(--accent); }
.callout.danger .callout-label { color: var(--accent); }

/* TOP-5 grid */
.top-grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin: 16px 0 24px; }
.top-card { display: flex; gap: 16px; padding: 18px 20px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
.top-rank { width: 36px; height: 36px; border-radius: 50%; background: var(--accent); color: white; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.top-body h4 { margin: 0 0 6px; }
.top-body p { margin: 0; color: var(--muted); font-size: 14px; }

/* Tags */
.tag { display: inline-block; padding: 3px 10px; font-size: 11px; font-weight: 600; color: white; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.05em; }
.pill-list { list-style: none; padding: 0; margin: 8px 0 0; display: flex; flex-wrap: wrap; gap: 6px; }
.pill-list li { background: white; padding: 4px 10px; border-radius: 999px; font-size: 13px; }
.pill-list code { background: transparent; padding: 0; font-size: 13px; }

/* Data table */
.data-table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.data-table th { text-align: left; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); padding: 12px 16px; background: #f9fafb; border-bottom: 1px solid var(--border); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }
.data-table tr:last-child td { border-bottom: 0; }

/* Matrix */
.matrix { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; background: var(--surface); border: 1px solid var(--border); }
.matrix th { padding: 10px; text-align: center; background: #f9fafb; border-bottom: 1px solid var(--border); font-size: 12px; }
.matrix tbody th { text-align: right; padding-right: 12px; background: #fafaf9; font-weight: 600; }
.matrix td { padding: 10px; text-align: center; border: 1px solid var(--border); font-weight: 600; font-variant-numeric: tabular-nums; }

/* Bars */
.bar-row { display: grid; grid-template-columns: 100px 1fr 40px; gap: 12px; align-items: center; margin: 10px 0; }
.bar-name { font-weight: 600; font-size: 14px; }
.bar { background: #f3f4f6; height: 8px; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--accent); }
.bar-val { font-variant-numeric: tabular-nums; font-weight: 600; font-size: 14px; }

/* Ideas grid */
.ideas-grid, .lideas-grid, .landings-grid, .tests-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 16px; margin: 24px 0; }
.idea-card, .lidea-card, .landing-card, .test-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
.idea-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.idea-id { font-size: 12px; font-weight: 700; color: var(--muted); }
.idea-tags { display: flex; gap: 6px; }
.idea-card h4 { font-size: 18px; margin-bottom: 16px; }
.idea-line { display: grid; grid-template-columns: 60px 1fr; gap: 10px; font-size: 13px; margin: 6px 0; }
.idea-line .lbl { color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; padding-top: 2px; }
.idea-foot { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border); font-size: 12px; }

/* Landing cards */
.landing-card { padding: 24px; }
.landing-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; gap: 16px; }
.landing-head h4 { font-size: 18px; }
.score-circle { background: var(--accent-soft); color: var(--accent); width: 56px; height: 56px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; }
.score-n { font-size: 18px; font-weight: 800; line-height: 1; }
.score-l { font-size: 10px; opacity: 0.7; }
.landing-hero { background: #fafaf9; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px; }
.lh-label { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; color: var(--muted); margin-bottom: 6px; }
.lh-headline { font-weight: 600; margin-bottom: 6px; font-size: 15px; }
.lh-sub { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.lh-cta { font-size: 13px; margin: 0; }
.landing-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.landing-grid ul { margin: 0; padding-left: 18px; font-size: 13px; }
.landing-grid li { margin: 4px 0; }

/* Lidea cards (improvement ideas) */
.lidea-card { display: flex; gap: 14px; }
.lidea-rank { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); color: white; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.lidea-body h4 { font-size: 15px; line-height: 1.4; }
.lidea-body p { font-size: 13px; }
.lidea-tags { display: flex; gap: 6px; margin-top: 8px; }

/* Hypotheses */
.hyp { display: flex; gap: 24px; padding: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; margin: 12px 0; }
.hyp-num { font-size: 48px; font-weight: 800; color: var(--accent); flex-shrink: 0; line-height: 1; letter-spacing: -0.02em; }
.hyp-body { flex: 1; }
.hyp-body h3 { margin: 0 0 12px; font-size: 18px; }
.verdict { display: inline-block; padding: 4px 12px; font-size: 12px; font-weight: 700; letter-spacing: 0.05em; border-radius: 4px; margin-bottom: 12px; }
.verdict.pass { background: #d1fae5; color: #065f46; }
.hyp-stats { display: flex; gap: 24px; margin: 12px 0; font-size: 14px; }
.hyp-stats strong { font-size: 20px; color: var(--accent); display: block; }

/* Tests */
.test-card { padding: 20px; }
.test-head { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px; }
.test-head h4 { margin: 0; }
.test-card p { font-size: 13px; margin: 6px 0; }

/* Lists */
ol.big-list { padding-left: 20px; }
ol.big-list li { margin: 10px 0; }

/* Method steps */
.method-steps { display: flex; flex-direction: column; gap: 12px; margin: 20px 0; }
.method-step { display: flex; gap: 16px; padding: 16px 20px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
.method-step .ms-num { flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%; background: var(--accent); color: white; font-weight: 700; display: flex; align-items: center; justify-content: center; font-variant-numeric: tabular-nums; }
.method-step strong { color: var(--text); }
.method-step em { color: var(--accent); font-style: normal; font-weight: 600; }
"""

JS = """
const sections = document.querySelectorAll('section');
const links = document.querySelectorAll('nav.sidebar a');
const linkMap = {};
links.forEach(l => { linkMap[l.getAttribute('href').slice(1)] = l; });

const observer = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if (en.isIntersecting) {
      links.forEach(l => l.classList.remove('active'));
      const link = linkMap[en.target.id];
      if (link) link.classList.add('active');
    }
  });
}, { rootMargin: '-30% 0px -65% 0px' });

sections.forEach(s => observer.observe(s));
"""


# ----- Compose -----
nav_items = [
    ("hero", "Обзор"),
    ("about", "О чём это исследование"),
    ("summary", "Главные выводы"),
    ("competitors", "Карта конкурентов"),
    ("creatives", "Разбор рекламы"),
    ("ideas", "10 идей рекламы"),
    ("traffic", "Каналы продвижения"),
    ("landings", "Посадочные страницы"),
    ("hypotheses", "Гипотезы"),
    ("tests", "План тестов"),
    ("emigrants", "Эмигранты в EU и Израиле"),
    ("meta", "Источники"),
]
nav_html = "".join(f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in nav_items)

body = (
    section_hero()
    + section_about()
    + section_summary()
    + section_competitors()
    + section_creatives()
    + section_ideas()
    + section_traffic()
    + section_landings()
    + section_hypotheses()
    + section_tests()
    + section_emigrants()
    + section_meta()
)

html_doc = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Языковой барьер · Конкурентный анализ · 2026-05-12</title>
<style>{CSS}</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <div class="brand">Языковой барьер · 2026-05-12</div>
    <ol>{nav_html}</ol>
  </nav>
  <main>{body}</main>
</div>
<script>{JS}</script>
</body>
</html>
"""

OUT.write_text(html_doc, encoding="utf-8")
print(f"Wrote {OUT} ({len(html_doc):,} bytes)")
