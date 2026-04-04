#!/usr/bin/env python3
"""Insert interpretation toggles before each lab group table."""

import re

HTML = './/05_SITE/index.html'

# ── Summaries ──────────────────────────────────────────────────────────────
# Each key matches a data-bg-group attribute in index.html.
# Value: (last_year_summary, all_time_summary, clinical_meaning)
# Replace these with your own interpretations based on your lab data.
SUMMARIES = {
    'rbc': (
        'Пример: Гемоглобин в норме (130 г/л). Эритроциты и гематокрит стабильны.',
        'Пример: За весь период наблюдения показатели красной крови в пределах нормы.',
        'Пример: Анемии нет. MCV и MCH нормальны — нет признаков железодефицита.',
    ),
    'plt': (
        'Пример: Тромбоциты стабильно в норме (200–260 тыс/мкл).',
        'Пример: Тромбоциты в норме на протяжении всего периода наблюдения.',
        'Пример: Гемостатическая система работает устойчиво.',
    ),
    'wbc': (
        'Пример: Лейкоциты в норме. Лейкоцитарная формула без отклонений.',
        'Пример: Лейкоциты стабильны. Нейтрофилы и лимфоциты в пределах нормы.',
        'Пример: Иммунная система без видимых отклонений.',
    ),
    # Add more groups as needed: 'inf', 'bb-electro', 'bb-renal', 'bb-liver',
    # 'bb-protein', 'bb-glucose', 'bb-lipid', 'bb-enzymes', 'bb-iron',
    # 'bb-inflam', 'coag-main', 'fat', 'bvit', 'wsvit', 'vitlike',
    # 'urine-phys', 'urine-chem', 'urine-sediment', 'urine-crystals',
    # 'urine-micro', 'horm-thyroid', 'horm-thyroid-ab', 'horm-repro',
    # 'horm-adrenal', 'horm-metabolic', 'horm-gh', 'horm-pth', 'horm-gi'
}

# ── CSS to add ─────────────────────────────────────────────────────────────
CSS = '''
  /* Group summary toggle */
  .gs-toggle { border-radius:8px; overflow:hidden; margin-bottom:.75rem; }
  .gs-toggle > summary {
    list-style:none; cursor:pointer; padding:.5rem .9rem;
    background:var(--bg-sub); border:1px solid var(--border);
    border-radius:8px; font-size:.78rem; font-weight:600;
    color:var(--text-3); text-transform:uppercase; letter-spacing:.05em;
    display:flex; align-items:center; gap:.4rem; user-select:none;
  }
  .gs-toggle > summary::-webkit-details-marker { display:none; }
  .gs-toggle > summary::before { content:"▸"; font-size:.7rem; transition:transform .15s; }
  .gs-toggle[open] > summary::before { transform:rotate(90deg); }
  .gs-toggle > summary:hover { background:var(--bg-hover); color:var(--text-2); }
  .gs-toggle[open] > summary {
    border-radius:8px 8px 0 0;
    border-bottom-color:var(--border-2);
  }
  .gs-body {
    display:grid; grid-template-columns:1fr 1fr 1fr; gap:0;
    border:1px solid var(--border); border-top:none;
    border-radius:0 0 8px 8px; overflow:hidden;
  }
  @media(max-width:700px){ .gs-body{ grid-template-columns:1fr; } }
  .gs-block {
    padding:.65rem .9rem; border-right:1px solid var(--border-2);
    background:var(--bg-card);
  }
  .gs-block:last-child { border-right:none; }
  .gs-label {
    font-size:.72rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.05em; color:var(--text-3); margin-bottom:.3rem;
  }
  .gs-text {
    font-size:.82rem; color:var(--text-2); line-height:1.5; margin:0;
  }
'''

# ── Main ───────────────────────────────────────────────────────────────────
with open(HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert CSS before /* Print button */
css_anchor = '  /* Print button */'
content = content.replace(css_anchor, CSS + '\n  /* Print button */', 1)

inserted = 0
for group_id, (last_year, all_time, meaning) in SUMMARIES.items():
    block = (
        '\n<details class="gs-toggle">'
        '<summary>Интерпретация динамики</summary>'
        '<div class="gs-body">'
        f'<div class="gs-block"><div class="gs-label">Последний год</div><p class="gs-text">{last_year}</p></div>'
        f'<div class="gs-block"><div class="gs-label">За всё время</div><p class="gs-text">{all_time}</p></div>'
        f'<div class="gs-block"><div class="gs-label">Что это значит</div><p class="gs-text">{meaning}</p></div>'
        '</div></details>\n'
    )
    # Find the group and insert before its first tbl-wrap
    pattern = (
        rf'(data-bg-group="{re.escape(group_id)}"[^>]*>.*?</summary>)'
        r'(\s*<div class="tbl-wrap lab-tbl-wrap">)'
    )
    new_content, n = re.subn(pattern, r'\1' + block + r'\2', content, count=1, flags=re.DOTALL)
    if n:
        content = new_content
        inserted += 1
        print(f'  ✓ {group_id}')
    else:
        print(f'  ✗ NOT FOUND: {group_id}')

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone: {inserted}/{len(SUMMARIES)} groups updated.')
