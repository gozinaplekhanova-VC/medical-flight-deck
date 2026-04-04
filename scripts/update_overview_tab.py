#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Overview tab redesign:
  1. Replace sec-ov HTML (remove emojis, new title, type badges, action lines, calmer ov-gaps)
  2. Add/update CSS (ov-type, ov-action, t-* trend variants, calmer chips, smaller ring)
  3. Update updateCriticalGaps() — priority groups
  4. Update toggleHIDetail() — remove emoji catLabels
  5. Create overview_rules.json
"""
import re, os

HTML = './05_SITE/index.html'
RULES_OUT = './02_TABLES/overview_rules.json'

with open(HTML, 'r', encoding='utf-8') as f:
    c = f.read()

# ── 1. REPLACE sec-ov ────────────────────────────────────────────────────────

OLD_SECOV_START = '  <div id="sec-ov" class="sec active">'
OLD_SECOV_END   = '  <div id="sec-bg" class="sec">'

NEW_SECOV = '''  <div id="sec-ov" class="sec active">
    <p class="section-title">Главное сейчас</p>

    <div class="ov-stats">
      <div class="ov-stat">
        <div class="ov-stat-label">Индекс здоровья</div>
        <div class="ov-score-wrap">
          <div class="ov-ring" id="hi-ring"><span class="ov-ring-val" id="hi-pct">…</span></div>
          <div>
            <div class="ov-stat-val" style="font-size:1.25rem" id="hi-pct2">…</div>
            <div class="ov-stat-sub" id="hi-sub">считается…</div>
          </div>
        </div>
      </div>
      <div class="ov-stat">
        <div class="ov-stat-label">Требуют действия</div>
        <div class="ov-stat-val" style="color:#ef4444" id="hi-crit">…</div>
        <div class="ov-stat-sub" id="hi-crit-sub" style="font-size:.72rem">из CHARTS</div>
      </div>
      <div class="ov-stat">
        <div class="ov-stat-label">Под мониторингом</div>
        <div class="ov-stat-val" style="color:#f59e0b" id="hi-imp">…</div>
        <div class="ov-stat-sub" id="hi-imp-sub" style="font-size:.72rem">из CHARTS</div>
      </div>
      <div class="ov-stat">
        <div class="ov-stat-label">Обновлено</div>
        <div class="ov-stat-val" style="font-size:1rem;padding-top:.3rem" id="hi-lastdate">…</div>
        <div class="ov-stat-sub" id="hi-lastsub"></div>
      </div>
    </div>

    <div class="ov-clusters">

      <!-- АНЕМИЯ — активный вопрос, янв 2026 -->
      <div class="ov-cluster cl-red">
        <div class="ov-cluster-head">
          <span class="ov-cluster-title">Анемия нормоцитарная</span>
          <span class="ov-type ot-issue">активный вопрос</span>
        </div>
        <div class="ov-cluster-trend">
          <span class="ov-trend t-urgent">↗ нарастает</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Hgb — белок эритроцитов, переносящий кислород. ↓ → анемия (усталость, одышка, бледность); ↑ → полицитемия.">Гемоглобин</span> — <span class="badge badge-low" style="font-size:.76rem">113 г/л ↓</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="RBC — красные клетки крови, переносят О₂ к тканям. ↓ → анемия; ↑ → полицитемия или дегидратация.">Эритроциты</span> — <span class="badge badge-low" style="font-size:.76rem">3.6 ↓</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Hct — доля объёма, занятая эритроцитами. ↓ → анемия; ↑ → сгущение крови (дегидратация, полицитемия).">Гематокрит</span> — <span class="badge badge-low" style="font-size:.76rem">34% ↓</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <p class="ov-note">Ферритин нормализован (14→86 ng/mL) — железодефицит исключён. МСН, МСV в норме — нормоцитарная нормохромная анемия. Возможно: анемия хронических заболеваний или аутоиммунный процесс.</p>
        <p class="ov-action">Следующий шаг: повтор ОАК + ретикулоциты, исключить хроническое заболевание.</p>
      </div>

      <!-- ИММУННЫЙ ДИСБАЛАНС — мониторинг -->
      <div class="ov-cluster cl-orange">
        <div class="ov-cluster-head">
          <span class="ov-cluster-title">Иммунный дисбаланс</span>
          <span class="ov-type ot-monitor">под мониторингом</span>
        </div>
        <div class="ov-cluster-trend">
          <span class="ov-trend t-watch">↔ 4 года стабильно</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Абс. число нейтрофилов — главные клетки-бойцы против бактерий. ↓ нейтропения → риск тяжёлых инфекций; ↑ → бактериальное воспаление.">Нейтрофилы абс.</span> — <span class="badge badge-low" style="font-size:.76rem">1.45 ↓</span></span>
          <span class="ov-abn-date">2025-10-01</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="% нейтрофилов в лейкоцитарной формуле. ↓ относительная нейтропения; ↑ → инфекция, воспаление, стресс.">Нейтрофилы%</span> — <span class="badge badge-low" style="font-size:.76rem">31.5% ↓</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="% лимфоцитов (T, B, NK). ↑ → вирусная инфекция, хроническое воспаление; ↓ → иммунодепрессия, стресс.">Лимфоциты%</span> — <span class="badge badge-high" style="font-size:.76rem">53.5% ↑</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="ECP — маркер активации эозинофилов. ↑ → аллергическое воспаление, паразитозы, эозинофильные заболевания. Норма &lt;24 нг/мл.">ECP</span> — <span class="badge badge-high" style="font-size:.76rem">84.1 нг/мл ↑</span></span>
          <span class="ov-abn-date">2025-09-20 (×3.5 нормы)</span>
        </div>
        <p class="ov-note">Нейтропения + лимфоцитоз — инверсионный паттерн на 10 датах за 4 года (2022–2026). Эозинофилы% нормализовались (4.4%, янв 2026) — но ECP по-прежнему высокий. Возможные причины: хроническая аллергия (D. farinae 4+), Blastocystis, аутоиммунный фон.</p>
        <p class="ov-action">Следующий шаг: иммунограмма (субпопуляции лимфоцитов) + консультация аллерголога.</p>
      </div>

      <!-- ГИПЕРХОЛЕСТЕРИНЕМИЯ — активный вопрос -->
      <div class="ov-cluster cl-amber">
        <div class="ov-cluster-head">
          <span class="ov-cluster-title">Гиперхолестеринемия</span>
          <span class="ov-type ot-issue">активный вопрос</span>
        </div>
        <div class="ov-cluster-trend">
          <span class="ov-trend t-watch">↔ стабильно повышен</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Total cholesterol — суммарный холестерин. ↑ → риск атеросклероза и ССЗ; на уровень влияют диета, генетика, гормоны.">Холестерин общий</span> — <span class="badge badge-high" style="font-size:.76rem">6.57 ↑</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="LDL — «плохой» холестерин, основной фактор образования атеросклеротических бляшек. Цель: &lt;3,0 ммоль/л; ↑ → риск инфаркта и инсульта.">ЛПНП (LDL)</span> — <span class="badge badge-high" style="font-size:.76rem">4.29 ↑</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Тестостерон у женщин вырабатывается яичниками и надпочечниками. ↑ → гиперандрогения, снижение активности рецепторов ЛПНП, рост ЛПНП.">Тестостерон</span> — <span class="badge badge-high" style="font-size:.76rem">2.17 нмоль/л ↑</span></span>
          <span class="ov-abn-date">2025-09-07 (норма 0.31–1.9)</span>
        </div>
        <p class="ov-note">ЛПНП 1.66× выше нормы, стабильно с 2024. Тестостерон ↑ после отмены КОК (июнь 2025) → вероятный основной механизм ЛПНП↑. Флуктуация дек 2025 (норма) → янв 2026 (↑) требует верификации. ЛПВП 1.76 — норма. ТГ 1.76 — в норме.</p>
        <p class="ov-action">Следующий шаг: сдать Лп(а), АпоB, рассчитать ФРС — оценка риска ССЗ.</p>
      </div>

      <!-- ИНФЕКЦИЯ И МАРКЕРЫ — мониторинг (бывш. «Прочие отклонения») -->
      <div class="ov-cluster cl-slate">
        <div class="ov-cluster-head">
          <span class="ov-cluster-title">Инфекция и маркеры</span>
          <span class="ov-type ot-monitor">под мониторингом</span>
        </div>
        <div class="ov-cluster-trend">
          <span class="ov-trend t-watch">↔ актуально</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Лейкоциты в моче — маркер воспаления МВП. 20–25/п.зр. при норме &lt;5 → пиурия, признак инфекции или воспаления. Посев мочи (2025-09-07): S. agalactiae 10³ КОЕ/мл.">Лейкоциты в моче</span> — <span class="badge badge-high" style="font-size:.76rem">20–25/п.зр. ↑</span></span>
          <span class="ov-abn-date">2025-10-13</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Klebsiella pneumoniae в посеве носа. ≥10⁴ — клинически значимая колонизация. Чувствительна к амикацину, амоксиклаву, левофлоксацину. Связана с хроническим риносинуситом.">Klebsiella pneumoniae (нос)</span> — <span class="badge badge-high" style="font-size:.76rem">10⁵ КОЕ/мл ↑</span></span>
          <span class="ov-abn-date">2025-10-13</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p3"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="% моноцитов — клеток врождённого иммунитета. ↑ → хроническое воспаление, вирусные инфекции, аутоиммунные состояния.">Моноциты%</span> — <span class="badge badge-high" style="font-size:.76rem">9.9% ↑</span></span>
          <span class="ov-abn-date">2026-01-12</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p2"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Витамин D (25-OH) — субоптимальный уровень &lt;75 нмоль/л. ↓ → иммунный дисбаланс, снижение ЛПВП-активности, повышение ЛПНП, хроническая усталость. Цель ≥100 нмоль/л.">Витамин D (25-OH)</span> — <span class="badge badge-low" style="font-size:.76rem">74.4 нмоль/л ↓</span></span>
          <span class="ov-abn-date">2025-07-24 (требует обновления)</span>
        </div>
        <p class="ov-note">АЛТ нормализовался (103→11 U/L, окт–янв). Натрий, RDW-CV, эозинофилы — нормализовались. Лейкоциты в моче + S. agalactiae → контроль ОАМ повтором. HLA-B27: носительство без клинического значения (ревматолог 2025, невролог 2026).</p>
        <p class="ov-action">Следующий шаг: повтор ОАМ + актуальный Витамин D (25-OH).</p>
      </div>

      <!-- ЖКТ / МИКРОБИОМ — активный вопрос -->
      <div class="ov-cluster cl-teal">
        <div class="ov-cluster-head">
          <span class="ov-cluster-title">ЖКТ и микробиом</span>
          <span class="ov-type ot-issue">активный вопрос</span>
        </div>
        <div class="ov-cluster-trend">
          <span class="ov-trend t-urgent">↗ персистирует</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Blastocystis spp. — кишечный паразит. Клиническое значение при симптоматике. Не поддаётся эрадикации с 2023 — 3 подтверждения (2023, 2024, 2025).">Blastocystis spp.</span> — <span class="badge badge-high" style="font-size:.76rem">обнаружен ↑</span></span>
          <span class="ov-abn-date">2025-09-07 (рецидив с 2023)</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p1"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Дисбиоз кишечника — нарушение состава микрофлоры. Bifidobacterium и Akkermansia muciniphila практически = 0 (Synnova, авг 2025). Akkermansia ассоциирована со снижением ЛПНП.">Дисбиоз (Bifidobacterium/Akkermansia)</span> — <span class="badge badge-high" style="font-size:.76rem">≈ 0 ↓↓</span></span>
          <span class="ov-abn-date">2025-08 (Synnova PCR)</span>
        </div>
        <div class="ov-abn-row">
          <span class="prio-dot p3"></span>
          <span class="ov-abn-name"><span class="tip" data-tip="Споры гриба в копрограмме — возможный кандидоз кишечника. Клиническое значение зависит от симптоматики и уровня.">Споры гриба (копрограмма)</span> — <span class="badge badge-high" style="font-size:.76rem">обнаружены</span></span>
          <span class="ov-abn-date">2025-09-07</span>
        </div>
        <p class="ov-note">Кальпротектин &lt;25 мкг/г (сент 2025) — органического воспаления нет. C. difficile ранее (окт 2024) — подтверждение эрадикации не документировано. Дисбиоз связывается с гиперхолестеринемией через нарушение метаболизма желчных кислот.</p>
        <p class="ov-action">Следующий шаг: гастроэнтеролог — стратегия эрадикации Blastocystis + восстановление микробиома.</p>
      </div>

    </div>

    <div class="ov-gaps">
      <div class="ov-gaps-title" id="ov-gaps-title">Рекомендованные анализы</div>
      <div id="ov-gaps-chips"><!-- заполняется JS --></div>
    </div>

    <p style="margin-top:.9rem;font-size:.76rem;color:var(--text-4)">Это не медицинский совет. Проконсультируйтесь с врачом.</p>
  </div>

  '''

start_idx = c.index(OLD_SECOV_START)
end_idx   = c.index(OLD_SECOV_END)
c = c[:start_idx] + NEW_SECOV + c[end_idx:]
print('sec-ov replaced: %d chars → %d chars' % (end_idx - start_idx, len(NEW_SECOV)))

# ── 2. CSS UPDATES ────────────────────────────────────────────────────────────

# 2a. Make ov-ring smaller
OLD_RING = '''  .ov-ring {
    width: 52px; height: 52px; border-radius: 50%; flex-shrink: 0;
    background: conic-gradient(#10b981 0% 82%, var(--border) 82% 100%);
    display: flex; align-items: center; justify-content: center; position: relative;
    transition: background .4s ease;
  }
  .ov-ring::after {
    content: ''; position: absolute; width: 38px; height: 38px;
    background: var(--bg-card); border-radius: 50%;
  }
  .ov-ring-val {
    position: relative; z-index: 1; font-size: .78rem; font-weight: 700; color: var(--text);
  }'''

NEW_RING = '''  .ov-ring {
    width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0;
    background: conic-gradient(#10b981 0% 82%, var(--border) 82% 100%);
    display: flex; align-items: center; justify-content: center; position: relative;
    transition: background .4s ease;
  }
  .ov-ring::after {
    content: ''; position: absolute; width: 32px; height: 32px;
    background: var(--bg-card); border-radius: 50%;
  }
  .ov-ring-val {
    position: relative; z-index: 1; font-size: .72rem; font-weight: 700; color: var(--text);
  }'''

assert OLD_RING in c, 'ERROR: ov-ring CSS not found'
c = c.replace(OLD_RING, NEW_RING, 1)
print('ov-ring: resized')

# 2b. Calm down ov-gaps left border (orange → slate)
OLD_GAPS_CSS = '''  .ov-gaps {
    background: var(--bg-card); border: 1px solid var(--border);
    border-left: 4px solid #f97316; border-radius: 10px;
    padding: .9rem 1.1rem; box-shadow: 0 1px 3px var(--shadow);
  }'''

NEW_GAPS_CSS = '''  .ov-gaps {
    background: var(--bg-card); border: 1px solid var(--border);
    border-left: 4px solid #94a3b8; border-radius: 10px;
    padding: .9rem 1.1rem; box-shadow: 0 1px 3px var(--shadow);
  }'''

assert OLD_GAPS_CSS in c, 'ERROR: ov-gaps CSS not found'
c = c.replace(OLD_GAPS_CSS, NEW_GAPS_CSS, 1)
print('ov-gaps: border calmed')

# 2c. Calm down ov-chip colors + add new classes after .dark .ov-chip
OLD_CHIP_CSS = '''  .ov-chip {
    font-size: .76rem; background: #fff7ed; color: #9a3412;
    border: 1px solid #fed7aa; border-radius: 20px; padding: .18rem .55rem;
  }
  .dark .ov-chip { background: #431407; color: #fdba74; border-color: #7c2d12; }'''

NEW_CHIP_CSS = '''  .ov-chip {
    font-size: .76rem; background: var(--bg-2,#f1f5f9); color: var(--text-2);
    border: 1px solid var(--border); border-radius: 20px; padding: .18rem .55rem;
  }
  .dark .ov-chip { background: #1e293b; color: var(--text-2); border-color: var(--border); }
  /* ov-type badges */
  .ov-type {
    font-size: .67rem; font-weight: 600; padding: .12rem .45rem;
    border-radius: 20px; text-transform: uppercase; letter-spacing: .04em;
    white-space: nowrap; flex-shrink: 0;
  }
  .ot-issue   { background: #fee2e2; color: #991b1b; }
  .ot-monitor { background: #fef9c3; color: #713f12; }
  .ot-check   { background: #dbeafe; color: #1e40af; }
  .dark .ot-issue   { background: #450a0a; color: #fca5a5; }
  .dark .ot-monitor { background: #422006; color: #fcd34d; }
  .dark .ot-check   { background: #172554; color: #93c5fd; }
  /* ov-trend variants */
  .ov-trend.t-urgent   { background: #fee2e2; color: #991b1b; }
  .ov-trend.t-active   { background: #ffedd5; color: #9a3412; }
  .ov-trend.t-watch    { background: #f1f5f9; color: #475569; }
  .ov-trend.t-check    { background: #eff6ff; color: #1d4ed8; }
  .ov-trend.t-improving{ background: #f0fdf4; color: #166534; }
  .dark .ov-trend.t-watch { background: #1e293b; color: #94a3b8; }
  /* cluster sub-elements */
  .ov-cluster-trend { margin-bottom: .55rem; }
  .ov-action {
    margin-top: .4rem; font-size: .76rem; color: var(--text-2);
    padding-top: .35rem; border-top: 1px solid var(--border-2);
    font-weight: 500;
  }
  /* recommended tests priority groups */
  .ov-chips-group { margin-bottom: .5rem; }
  .ov-chips-group:last-child { margin-bottom: 0; }
  .ov-chips-label {
    display: block; font-size: .68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .05em;
    color: var(--text-3); margin-bottom: .3rem;
  }'''

assert OLD_CHIP_CSS in c, 'ERROR: ov-chip CSS not found'
c = c.replace(OLD_CHIP_CSS, NEW_CHIP_CSS, 1)
print('ov-chip: calmed + new CSS classes added')

# ── 3. UPDATE updateCriticalGaps() ──────────────────────────────────────────

OLD_GAPS_JS = r"""function updateCriticalGaps() {
  var chipsEl = document.getElementById('ov-gaps-chips');
  var titleEl = document.getElementById('ov-gaps-title');
  if (!chipsEl) return;

  var items = document.querySelectorAll('#sec-rec .rec-tests-grid .rec-test-item');
  if (!items.length) {
    chipsEl.innerHTML = '<span style="color:var(--ok,#22c55e);font-size:.85rem;font-weight:600">✓ Список рекомендаций пуст</span>';
    if (titleEl) titleEl.textContent = '✓ Рекомендованные анализы';
    return;
  }

  if (titleEl) titleEl.textContent = '⚠️ Рекомендованные анализы (' + items.length + ')';

  chipsEl.innerHTML = Array.from(items).map(function(item) {
    var prioEl = item.querySelector('.prio-dot');
    var m = prioEl && prioEl.className.match(/p\d/);
    var prio = m ? m[0] : 'p3';
    var tipEl = item.querySelector('.tip');
    var tip = tipEl ? tipEl.getAttribute('data-tip') : '';
    var name = tipEl ? tipEl.textContent.trim() : item.textContent.trim();
    return '<span class="ov-chip"><span class="tip" data-tip="' + tip.replace(/"/g, '&quot;') + '">'
      + '<span class="prio-dot ' + prio + '" style="vertical-align:middle;display:inline-block;margin-right:4px"></span>'
      + name + '</span></span>';
  }).join('');
}"""

NEW_GAPS_JS = r"""function updateCriticalGaps() {
  var chipsEl = document.getElementById('ov-gaps-chips');
  var titleEl = document.getElementById('ov-gaps-title');
  if (!chipsEl) return;

  var items = document.querySelectorAll('#sec-rec .rec-tests-grid .rec-test-item');
  if (!items.length) {
    chipsEl.innerHTML = '<span style="color:var(--ok,#22c55e);font-size:.85rem;font-weight:600">Список рекомендаций пуст</span>';
    if (titleEl) titleEl.textContent = 'Рекомендованные анализы';
    return;
  }

  if (titleEl) titleEl.textContent = 'Рекомендованные анализы (' + items.length + ')';

  var p1 = [], p23 = [];
  Array.from(items).forEach(function(item) {
    var prioEl = item.querySelector('.prio-dot');
    var m = prioEl && prioEl.className.match(/p\d/);
    var prio = m ? m[0] : 'p3';
    var tipEl = item.querySelector('.tip');
    var tip = tipEl ? tipEl.getAttribute('data-tip') : '';
    var name = tipEl ? tipEl.textContent.trim() : item.textContent.trim();
    var chip = '<span class="ov-chip"><span class="tip" data-tip="' + tip.replace(/"/g, '&quot;') + '">'
      + '<span class="prio-dot ' + prio + '" style="vertical-align:middle;display:inline-block;margin-right:4px"></span>'
      + name + '</span></span>';
    if (prio === 'p1') { p1.push(chip); } else { p23.push(chip); }
  });

  var html = '';
  if (p1.length) {
    html += '<div class="ov-chips-group"><span class="ov-chips-label">Срочно</span>'
      + '<div class="ov-chips">' + p1.join('') + '</div></div>';
  }
  if (p23.length) {
    html += '<div class="ov-chips-group"><span class="ov-chips-label">Плановые</span>'
      + '<div class="ov-chips">' + p23.join('') + '</div></div>';
  }
  chipsEl.innerHTML = html;
}"""

assert OLD_GAPS_JS in c, 'ERROR: updateCriticalGaps() not found'
c = c.replace(OLD_GAPS_JS, NEW_GAPS_JS, 1)
print('updateCriticalGaps: updated with priority groups')

# ── 4. UPDATE toggleHIDetail() — remove emoji catLabels ──────────────────────

OLD_CATLABEL = "  var catLabel = { critical:'🔴 Критическое', strong:'🟠 Сильное',\n                   moderate:'🟡 Умеренное', border:'🔵 Пограничное' };"
NEW_CATLABEL = "  var catLabel = { critical:'Критическое', strong:'Сильное',\n                   moderate:'Умеренное', border:'Пограничное' };"

assert OLD_CATLABEL in c, 'ERROR: catLabel not found'
c = c.replace(OLD_CATLABEL, NEW_CATLABEL, 1)
print('toggleHIDetail: emoji catLabels removed')

# ── 5. SAVE index.html ────────────────────────────────────────────────────────

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(c)
print('index.html saved.')

# ── 6. CREATE overview_rules.json ─────────────────────────────────────────────

rules = '''{
  "_description": "Selection rules for the Overview tab (Главное сейчас). Defines what qualifies for each cluster card and card type.",
  "_updated": "2026-03-27",

  "card_types": {
    "active_issue":      "Confirmed, current abnormality requiring action or active clinical follow-up.",
    "monitor":           "Persistent abnormality, stable — watch for change but no immediate action needed.",
    "improving":         "Was abnormal, now trending toward normal — document progress.",
    "background_risk":   "Genetic marker or historical finding with no current clinical significance.",
    "pending_check":     "Test result overdue or not yet obtained — gap in monitoring."
  },

  "status_pills": {
    "t-urgent":   "Actively worsening or newly detected — needs action soon.",
    "t-active":   "Stable but flagged as active issue — keep visible.",
    "t-watch":    "Stable for ≥2 measurements — monitoring only.",
    "t-check":    "Pending verification or retest.",
    "t-improving":"Trend clearly improving over ≥2 measurements."
  },

  "type_badges": {
    "ot-issue":   "активный вопрос — red badge",
    "ot-monitor": "под мониторингом — amber badge",
    "ot-check":   "требует проверки — blue badge"
  },

  "inclusion_rules": {
    "must_include": [
      "Any parameter with status=critical or status=strong in CHARTS (latest value)",
      "Any cluster where ≥2 related abnormalities are grouped",
      "Any infection marker confirmed by culture or PCR in last 12 months"
    ],
    "may_include": [
      "Moderate abnormalities (status=moderate) if clinically linked to active cluster",
      "Genetic markers only as ov-note background_risk — never as ov-abn-row"
    ],
    "exclude": [
      "Normalized values (previously abnormal, now within range for ≥2 measurements)",
      "Duplicate representation of same finding across clusters",
      "Historical one-time anomalies without recurrence"
    ]
  },

  "clusters": {
    "cl-red":    "Critical/urgent — active issue worsening",
    "cl-orange": "High concern — persistent immune/inflammatory pattern",
    "cl-amber":  "Moderate concern — metabolic or lipid issue",
    "cl-slate":  "Mixed/infectious markers — monitoring",
    "cl-teal":   "GI/microbiome — specialist referral needed"
  }
}
'''

with open(RULES_OUT, 'w', encoding='utf-8') as f:
    f.write(rules)
print('overview_rules.json created at', RULES_OUT)
print('Done.')
