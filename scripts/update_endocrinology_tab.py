#!/usr/bin/env python3
"""Restructure sec-hormones → Эндокринолог tab. Also update CSV files."""

import re, os

INDEX = './05_SITE/index.html'
HORMONES_CSV = './02_TABLES/hormones.csv'
VITAMINS_CSV  = './02_TABLES/vitamins.csv'

# ── 1. index.html ─────────────────────────────────────────────────────────────
with open(INDEX, 'r', encoding='utf-8') as f:
    html = f.read()

# 1a. GROUPS: add coag
old_g = "'bg':'analyses','bb':'analyses','vit':'analyses','urine':'analyses','hormones':'analyses','other':'analyses',"
new_g = "'bg':'analyses','bb':'analyses','coag':'analyses','vit':'analyses','urine':'analyses','hormones':'analyses','other':'analyses',"
if old_g in html:
    html = html.replace(old_g, new_g, 1)
    print("GROUPS: added coag")
else:
    print("GROUPS: coag already present or pattern not found")

# 1b. Rename button
old_btn = '>Гормоны </button>'
new_btn = '>Эндокринолог </button>'
n = html.count(old_btn)
if n == 1:
    html = html.replace(old_btn, new_btn, 1)
    print("Button: renamed to Эндокринолог")
else:
    print(f"Button: pattern count={n}, skipping")

# 1c. Replace sec-hormones
start_marker = '  <div id="sec-hormones" class="sec">'
end_marker   = '\n  <div id="sec-meds" class="sec">'
si = html.index(start_marker)
ei = html.index(end_marker)
old_len = ei - si
print(f"Replacing sec-hormones: {old_len} chars")

NEW_SEC = '''  <div id="sec-hormones" class="sec">
    <p class="section-title">Эндокринолог</p>

    <!-- 1. Щитовидная железа -->
    <details class="bg-group" open data-bg-group="horm-thyroid">
      <summary class="bg-group-sum"><span class="bg-group-label">🦋 Щитовидная железа</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2023-07-10</th><th>2024-03-05</th><th>2024-03-19</th><th>2024-07-22</th><th>2025-08-25</th><th>2025-09-20</th><th>2026-01-12</th>
      </tr></thead><tbody>
      <tr data-prio="1">
        <td class="prio-cell"><span class="prio-dot p1" title="Критичный"></span></td>
        <td class="test-name"><span class="tip" data-tip="ТТГ (TSH) — тиреотропный гормон гипофиза. Первичный скрининг функции щитовидной железы. ↑ → гипотиреоз; ↓ → гипертиреоз.">ТТГ (TSH)</span></td>
        <td class="unit">мЕд/л</td><td class="norm">0.27 – 4.20</td>
        <td><span class="badge badge-ok">2.70</span></td>
        <td><span class="badge badge-ok">1.52</span></td>
        <td><span class="badge badge-ok">2.32</span></td>
        <td><span class="badge badge-ok">1.41</span></td>
        <td><span class="badge badge-ok">1.96</span></td>
        <td><span class="badge badge-ok">0.96</span></td>
        <td><span class="badge badge-ok">1.81</span></td>
      </tr>
      <tr data-prio="1">
        <td class="prio-cell"><span class="prio-dot p1" title="Критичный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Т4 свободный (FT4) — основной тиреоидный гормон. Снижен при первичном гипотиреозе. Разные лаборатории используют пмоль/л или нг/дл.">Т4 свободный (FT4)</span></td>
        <td class="unit">пмоль/л</td><td class="norm">9.0 – 22.0</td>
        <td class="empty">—</td>
        <td><span class="badge badge-low" title="нг/дл; лаб. норма 0.92–1.68 нг/дл; пересчёт ≈ 10.7 пмоль/л">0.83 нг/дл ↓</span></td>
        <td><span class="badge badge-low" title="нг/дл; лаб. норма 0.92–1.68 нг/дл; пересчёт ≈ 10.3 пмоль/л">0.80 нг/дл ↓</span></td>
        <td><span class="badge badge-ok">11.71</span></td>
        <td><span class="badge badge-ok">11.84</span></td>
        <td><span class="badge badge-ok">9.28</span></td>
        <td><span class="badge badge-ok">13.77</span></td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Т3 свободный (FT3) — активная форма тиреоидного гормона. Оценивается при подозрении на конверсионную недостаточность T4→T3.">Т3 свободный (FT3)</span></td>
        <td class="unit">пмоль/л</td><td class="norm">2.0 – 6.8</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok" title="пг/мл; лаб. норма 2.0–4.4 пг/мл; пересчёт ≈ 3.3 пмоль/л">2.14 пг/мл</span></td>
        <td><span class="badge badge-ok" title="пг/мл; лаб. норма 2.0–4.4 пг/мл; пересчёт ≈ 3.4 пмоль/л">2.24 пг/мл</span></td>
        <td><span class="badge badge-ok">4.72</span></td>
        <td><span class="badge badge-ok">3.93</span></td>
        <td><span class="badge badge-ok">3.48</span></td>
        <td><span class="badge badge-ok">4.50</span></td>
      </tr>
      </tbody></table></div>
    </details>

    <!-- 2. Аутоиммунный скрининг щитовидной железы -->
    <details class="bg-group" open data-bg-group="horm-thyroid-ab">
      <summary class="bg-group-sum"><span class="bg-group-label">🛡️ Аутоиммунный скрининг щитовидной железы</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2023-03-04</th><th>2024-03-19</th><th>2024-07-22</th>
      </tr></thead><tbody>
      <tr data-prio="1">
        <td class="prio-cell"><span class="prio-dot p1" title="Критичный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Анти-ТПО — антитела к тиреоидной пероксидазе. Маркер аутоиммунного тиреоидита Хашимото. При повышении + симптомах гипотиреоза — показание к лечению.">Анти-ТПО</span></td>
        <td class="unit">МЕ/мл</td><td class="norm">&lt; 5.61</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">3.0</span></td>
        <td><span class="badge badge-ok">3.0</span></td>
      </tr>
      <tr data-prio="1">
        <td class="prio-cell"><span class="prio-dot p1" title="Критичный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Антитела к тиреоглобулину (АТ-ТГ) — дополнительный маркер аутоиммунного тиреоидита. Норма &lt; 115 МЕ/мл.">Антитела к тиреоглобулину (АТ-ТГ)</span></td>
        <td class="unit">МЕ/мл</td><td class="norm">&lt; 115</td>
        <td><span class="badge badge-ok">17.0</span></td>
        <td><span class="badge badge-ok">15.0</span></td>
        <td><span class="badge badge-ok">15.0</span></td>
      </tr>
      </tbody></table></div>
    </details>

    <!-- 3. Репродуктивные гормоны -->
    <details class="bg-group" open data-bg-group="horm-repro">
      <summary class="bg-group-sum"><span class="bg-group-label">♀️ Репродуктивные гормоны</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2023-07-10</th><th>2024-03-19</th><th>2025-09-07</th><th>2025-09-20</th>
      </tr></thead><tbody>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="ЛГ (LH) — лютеинизирующий гормон. Норма зависит от фазы цикла. ЛГ/ФСГ &gt; 2.0 — признак СПКЯ. Без фазы — интерпретация ограничена.">ЛГ</span></td>
        <td class="unit">мМЕ/мл</td><td class="norm">фаза цикла</td>
        <td class="empty">—</td>
        <td><span class="badge badge-unk">15.46</span></td>
        <td><span class="badge badge-unk">8.96</span></td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="ФСГ (FSH) — фолликулостимулирующий гормон. ↑ при снижении овариального резерва. 2023-07-10: 9.41 при норме 3.85–8.78 — выше нормы. Фаза цикла не указана.">ФСГ</span></td>
        <td class="unit">мМЕ/мл</td><td class="norm">фаза цикла</td>
        <td><span class="badge badge-high" title="норм 3.85–8.78 (фолликулярная фаза); фаза цикла не указана">9.41 ↑</span></td>
        <td><span class="badge badge-unk">10.15</span></td>
        <td><span class="badge badge-unk">8.36</span></td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Пролактин — гормон гипофиза. ↑ при стрессе, гипотиреозе, аденоме гипофиза, антидепрессантах. 2024-03-19: 44.11 нг/мл значительно выше нормы 4.79–23.3 нг/мл.">Пролактин</span></td>
        <td class="unit">мМЕ/л</td><td class="norm">108.8 – 557.1</td>
        <td class="empty">—</td>
        <td><span class="badge badge-high" title="44.11 нг/мл; норм 4.79–23.3 нг/мл; ≈ 935 мМЕ/л">44.11 нг/мл ↑</span></td>
        <td><span class="badge badge-ok">316.3</span></td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="3">
        <td class="prio-cell"><span class="prio-dot p3" title="Информативный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Эстрадиол (E2) — основной эстроген. Норма широко варьирует по фазе цикла. Без привязки к фазе — интерпретация ограничена.">Эстрадиол</span></td>
        <td class="unit">пмоль/л</td><td class="norm">фаза цикла</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td><span class="badge badge-unk">175.8</span></td>
        <td><span class="badge badge-unk">692.1</span></td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="АМГ (антимюллеров гормон) — маркер овариального резерва. Норма 0.07–7.35 нг/мл. Не зависит от фазы цикла и может измеряться в любой день.">АМГ</span></td>
        <td class="unit">нг/мл</td><td class="norm">0.07 – 7.35</td>
        <td><span class="badge badge-ok">1.91</span></td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">3.22</span></td>
        <td class="empty">—</td>
      </tr>
      </tbody></table></div>
    </details>

    <!-- 4. Андрогены и надпочечники -->
    <details class="bg-group" open data-bg-group="horm-adrenal">
      <summary class="bg-group-sum"><span class="bg-group-label">💪 Андрогены и надпочечники</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2024-03-19</th><th>2025-07-24</th><th>2025-09-07</th><th>2025-09-20</th>
      </tr></thead><tbody>
      <tr data-prio="1">
        <td class="prio-cell"><span class="prio-dot p1" title="Критичный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Тестостерон общий — у женщин норма 0.31–1.90 нмоль/л. Умеренное повышение возможно при СПКЯ, гиперандрогении надпочечников, инсулинорезистентности.">Тестостерон общий</span></td>
        <td class="unit">нмоль/л</td><td class="norm">0.31 – 1.90</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td><span class="badge badge-high">2.17 ↑</span></td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="ДГЭА-С (DHEA-S) — надпочечниковый андроген, маркер резерва надпочечников. ↓ при хроническом стрессе или гиперкортицизме.">ДГЭА-С</span></td>
        <td class="unit">мкг/дл</td><td class="norm">23 – 266</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">154.3</span></td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="АКТГ (кортикотропин) — гормон гипофиза, стимулирует кору надпочечников. Рассматривается вместе с кортизолом для дифференциации первичного и вторичного гиперкортицизма.">АКТГ</span></td>
        <td class="unit">пмоль/л</td><td class="norm">1.6 – 13.9</td>
        <td><span class="badge badge-ok">6.58</span></td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Кортизол утренний (забор 8:00–9:00) — пик суточного ритма кортизола. Норма 101–536 нмоль/л. 2024-03-19: 656.6 — выше нормы (хронический стресс или особенности забора).">Кортизол (утренний)</span></td>
        <td class="unit">нмоль/л</td><td class="norm">101.2 – 535.7</td>
        <td><span class="badge badge-high">656.6 ↑</span></td>
        <td><span class="badge badge-ok">361.4</span></td>
        <td class="empty">—</td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="3">
        <td class="prio-cell"><span class="prio-dot p3" title="Информативный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Кортизол (время забора не уточнено в источнике). Не эквивалентен утреннему — без привязки к времени суток интерпретация ограничена.">Кортизол</span></td>
        <td class="unit">нмоль/л</td><td class="norm">185 – 624</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">303.3</span></td>
      </tr>
      </tbody></table></div>
      <div style="margin:.5rem 0 .5rem 0;padding:.6rem 1rem;background:var(--bg-2);border-radius:6px;font-size:.82rem;color:var(--text-2)">
        <b>Кортизол слюна (2023-04-26) — суточный профиль:</b>
        после обеда <span class="badge badge-high">17.66 ↑</span> нмоль/л (норм 0–5.79) &nbsp;·&nbsp;
        вечер <span class="badge badge-high">5.79 ↑</span> (норм 0–4.14) &nbsp;·&nbsp;
        ночь <span class="badge badge-high">5.79 ↑</span> (норм 0–2.48) &nbsp;·&nbsp;
        <span style="color:var(--text-3)">все точки выше нормы — вероятен хронический гиперкортицизм или острый стресс-период</span>
      </div>
    </details>

    <!-- 5. Метаболическая эндокринология -->
    <details class="bg-group" open data-bg-group="horm-metabolic">
      <summary class="bg-group-sum"><span class="bg-group-label">🔬 Метаболическая эндокринология</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2024-03-19</th><th>2025-07-24</th><th>2025-09-07</th><th>2025-09-20</th>
      </tr></thead><tbody>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Инсулин натощак — базальный уровень инсулина. ↑ → инсулинорезистентность. Единицы различаются между лабораториями (мкМЕ/мл или пмоль/л).">Инсулин (натощак)</span></td>
        <td class="unit">мкМЕ/мл</td><td class="norm">2.6 – 24.9</td>
        <td><span class="badge badge-ok">4.7</span></td>
        <td><span class="badge badge-ok" title="51.4 пмоль/л ÷ 6.945 ≈ 7.4 мкМЕ/мл">~7.4 <small style="font-size:.7em">(пмоль/л)</small></span></td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">10.1</span></td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="C-пептид — маркер секреции собственного инсулина поджелудочной железой. Норма 0.78–5.19 нг/мл.">C-пептид</span></td>
        <td class="unit">нг/мл</td><td class="norm">0.78 – 5.19</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">1.14</span></td>
        <td class="empty">—</td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="HOMA-IR = (Глюкоза ммоль/л × Инсулин мкМЕ/мл) / 22.5. Норма &lt; 2.77. Индекс инсулинорезистентности.">Индекс HOMA-IR</span></td>
        <td class="unit">—</td><td class="norm">&lt; 2.77</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">2.06</span></td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Лептин — гормон насыщения, секретируется жировой тканью. ↓ при дефиците жировой массы, хроническом ограничении калорийности.">Лептин</span></td>
        <td class="unit">нг/мл</td><td class="norm">4.0 – 32.0</td>
        <td class="empty">—</td>
        <td class="empty">—</td>
        <td><span class="badge badge-low">3.66 ↓</span></td>
        <td class="empty">—</td>
      </tr>
      </tbody></table></div>
    </details>

    <!-- 6. Гормон роста / IGF-1 -->
    <details class="bg-group" open data-bg-group="horm-gh">
      <summary class="bg-group-sum"><span class="bg-group-label">📈 Гормон роста / IGF-1</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2024-03-05</th><th>2024-03-19</th><th>2024-07-22</th><th>2025-09-07</th>
      </tr></thead><tbody>
      <tr data-prio="3">
        <td class="prio-cell"><span class="prio-dot p3" title="Информативный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Гормон роста (GH, соматотропин) — разовый забор мало информативен из-за пульсирующей секреции. Норма 0.13–9.88 нг/мл.">Гормон роста (GH)</span></td>
        <td class="unit">нг/мл</td><td class="norm">0.13 – 9.88</td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok">0.997</span></td>
        <td class="empty">—</td>
        <td class="empty">—</td>
      </tr>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="IGF-1 (соматомедин-С) — суммарный маркер активности ГР за 2–3 нед. Норма 41–263 нг/мл. 2024-03-05: снижен по норме лаборатории (107–263 нг/мл). Данные хранились под именем Соматомедин-С (IGF-1) и IGF-1 — нормализовано до IGF-1.">IGF-1</span></td>
        <td class="unit">нг/мл</td><td class="norm">41 – 263</td>
        <td><span class="badge badge-low" title="мкг/л; лаб. норма 107–263 → снижен">96 ↓</span></td>
        <td class="empty">—</td>
        <td><span class="badge badge-ok" title="мкг/л; лаб. норма 41–246 → норма">68</span></td>
        <td><span class="badge badge-ok">103</span></td>
      </tr>
      </tbody></table></div>
    </details>

    <!-- 7. Кальций-фосфорный обмен -->
    <details class="bg-group" open data-bg-group="horm-pth">
      <summary class="bg-group-sum"><span class="bg-group-label">🦴 Кальций-фосфорный обмен</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2025-09-20</th>
      </tr></thead><tbody>
      <tr data-prio="2">
        <td class="prio-cell"><span class="prio-dot p2" title="Важный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Паратгормон (ПТГ) — регулятор кальций-фосфорного обмена. ↑ → гиперпаратиреоз (первичный или вторичный при дефиците Vit D). Норма 1.30–9.30 пмоль/л.">Паратгормон (ПТГ)</span></td>
        <td class="unit">пмоль/л</td><td class="norm">1.30 – 9.30</td>
        <td><span class="badge badge-ok">2.00</span></td>
      </tr>
      </tbody></table></div>
    </details>

    <!-- 8. ЖКТ-гормоны -->
    <details class="bg-group" open data-bg-group="horm-gi">
      <summary class="bg-group-sum"><span class="bg-group-label">🍽️ ЖКТ-гормоны</span><span class="bg-group-arrow">▾</span></summary>
      <div class="tbl-wrap lab-tbl-wrap"><table>
      <thead><tr>
        <th style="width:24px"></th><th>Показатель</th><th>Ед.</th><th>Норма</th>
        <th>2023-04-26</th>
      </tr></thead><tbody>
      <tr data-prio="3">
        <td class="prio-cell"><span class="prio-dot p3" title="Информативный"></span></td>
        <td class="test-name"><span class="tip" data-tip="Гастрин — гормон G-клеток антрального желудка. Стимулирует секрецию HCl. ↑ при гипергастринемии, атрофическом гастрите, гастриноме (синдром Золлингера–Эллисона).">Гастрин</span></td>
        <td class="unit">пг/мл</td><td class="norm">0 – 100</td>
        <td><span class="badge badge-ok">16</span></td>
      </tr>
      </tbody></table></div>
    </details>

  </div>'''

html = html[:si] + NEW_SEC + html[ei:]
print(f"sec-hormones replaced: {old_len} → {len(NEW_SEC)} chars")

# 1d. Add ENDOCRINOLOGY config after CBC_GROUPS
ENDOCRIN_CONFIG = '''
/* ── Endocrinology tab config (Эндокринолог / sec-hormones) ──────────────────
   Classification reference for agents and extractors.
   Update when adding new endocrine tests to hormones.csv.
   ─────────────────────────────────────────────────────────────────────────── */
var ENDOCRINOLOGY_SECTIONS = [
  { id:'horm-thyroid',    label:'Щитовидная железа',
    tests:['ТТГ (TSH)','Т4 свободный (FT4)','Т3 свободный (FT3)'] },
  { id:'horm-thyroid-ab', label:'Аутоиммунный скрининг щитовидной железы',
    tests:['Анти-ТПО','Антитела к тиреоглобулину (АТ-ТГ)'] },
  { id:'horm-repro',      label:'Репродуктивные гормоны',
    tests:['ЛГ','ФСГ','Пролактин','Эстрадиол','АМГ'] },
  { id:'horm-adrenal',    label:'Андрогены и надпочечники',
    tests:['Тестостерон общий','ДГЭА-С','АКТГ','Кортизол (утренний)','Кортизол',
           'Кортизол слюна (после обеда)','Кортизол слюна (вечер)','Кортизол слюна (ночь)'] },
  { id:'horm-metabolic',  label:'Метаболическая эндокринология',
    tests:['Инсулин (натощак)','C-пептид','Индекс HOMA-IR','Лептин'] },
  { id:'horm-gh',         label:'Гормон роста / IGF-1',
    tests:['Гормон роста (GH)','IGF-1'] },
  { id:'horm-pth',        label:'Кальций-фосфорный обмен',
    tests:['Паратгормон (ПТГ)'] },
  { id:'horm-gi',         label:'ЖКТ-гормоны',
    tests:['Гастрин'] }
];
/* Alias map: write canonical labels to hormones.csv, not aliases. */
var ENDOCRINOLOGY_ALIASES = {
  'ТТГ':'ТТГ (TSH)', 'TSH':'ТТГ (TSH)',
  'Т4 свободный':'Т4 свободный (FT4)', 'FT4':'Т4 свободный (FT4)',
  'Т3 свободный':'Т3 свободный (FT3)', 'FT3':'Т3 свободный (FT3)',
  'Anti-TPO':'Анти-ТПО', 'AT-TPO':'Анти-ТПО', 'АТ-ТПО':'Анти-ТПО',
  'АТ-ТГ':'Антитела к тиреоглобулину (АТ-ТГ)',
  'Соматомедин-С':'IGF-1', 'Соматомедин-С (IGF-1)':'IGF-1',
  'GH':'Гормон роста (GH)', 'Гормон роста':'Гормон роста (GH)',
  'LH':'ЛГ', 'FSH':'ФСГ', 'AMH':'АМГ',
  'Витамин B12':'Витамин B12' /* Belongs to vitamins.csv, NOT hormones.csv */
};
'''

cbc_end_marker = 'var bgCurrentFilter'
if html.count(cbc_end_marker) == 1:
    html = html.replace(cbc_end_marker, ENDOCRIN_CONFIG + '\nvar bgCurrentFilter', 1)
    print("ENDOCRINOLOGY_SECTIONS config added after CBC_GROUPS")
else:
    print(f"bgCurrentFilter count={html.count(cbc_end_marker)}, skipping config injection")

with open(INDEX, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html saved.")

# ── 2. hormones.csv: remove Витамин B12 row ───────────────────────────────────
with open(HORMONES_CSV, 'r', encoding='utf-8') as f:
    lines = f.readlines()

b12_rows = [l for l in lines if ',Витамин B12,' in l]
clean_lines = [l for l in lines if ',Витамин B12,' not in l]
# Also normalize "Соматомедин-С (IGF-1)" → "IGF-1"
clean_lines = [l.replace('Соматомедин-С (IGF-1)', 'IGF-1') for l in clean_lines]

with open(HORMONES_CSV, 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)
print(f"hormones.csv: removed {len(b12_rows)} B12 row(s); normalized Соматомедин-С → IGF-1")

# ── 3. vitamins.csv: add Витамин B12 row from hormones (if not already present) ─
with open(VITAMINS_CSV, 'r', encoding='utf-8') as f:
    vit_lines = f.readlines()

# Check if 2024-03-19 B12 already in vitamins.csv
already = any('2024-03-19' in l and 'Витамин B12' in l for l in vit_lines)
if not already and b12_rows:
    # Insert before last empty line or at end
    insert_line = b12_rows[0]  # 2024-03-19,Витамин B12,424.0,пмоль/л,...
    vit_lines.append(insert_line)
    with open(VITAMINS_CSV, 'w', encoding='utf-8') as f:
        f.writelines(vit_lines)
    print(f"vitamins.csv: added B12 row: {insert_line.strip()}")
else:
    print("vitamins.csv: B12 2024-03-19 already present or no row to add")

print("\nAll done.")
