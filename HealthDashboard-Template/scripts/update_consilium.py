#!/usr/bin/env python3
"""Redesign sec-consilium section and add new CSS classes."""

with open('.//05_SITE/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ─── 1. ADD NEW CSS CLASSES ───────────────────────────────────────────────
css_new = """\
  /* Consilium redesign */
  .cn-pills { display:inline-flex; flex-wrap:wrap; gap:.3rem; margin-left:.75rem; vertical-align:middle; }
  .cn-pill { font-size:.67rem; font-weight:600; background:var(--bg-2); color:var(--text-3); border-radius:20px; padding:.1rem .45rem; white-space:nowrap; border:1px solid var(--border); }
  .cn-section { margin-bottom:1.75rem; }
  .cn-section-label { font-size:.78rem; font-weight:700; color:var(--text-2); margin-bottom:.75rem; padding-bottom:.35rem; border-bottom:1px solid var(--border); }
  .cn-action-list { display:flex; flex-direction:column; gap:.5rem; }
  .cn-action-card { background:var(--bg-card); border-radius:8px; padding:.9rem 1.25rem; border:1px solid var(--border); box-shadow:0 1px 2px var(--shadow); display:flex; gap:.75rem; align-items:flex-start; }
  .cn-priority { font-size:.69rem; font-weight:700; border-radius:4px; padding:.15rem .45rem; white-space:nowrap; flex-shrink:0; margin-top:.15rem; }
  .cn-priority.p-urgent { background:#fee2e2; color:#991b1b; }
  .cn-priority.p-watch { background:#fef9c3; color:#713f12; }
  .cn-priority.p-plan { background:var(--bg-2); color:var(--text-3); border:1px solid var(--border); }
  .cn-priority.p-ok { background:#dcfce7; color:#166534; }
  .cn-action-body { flex:1; min-width:0; }
  .cn-action-title { font-weight:700; font-size:.88rem; margin-bottom:.2rem; color:var(--text); }
  .cn-action-title span { font-weight:400; color:var(--text-3); }
  .cn-action-note { font-size:.81rem; color:var(--text-3); line-height:1.5; }
  .cn-request { background:var(--bg-card); border-radius:8px; padding:.9rem 1.25rem; margin-bottom:1.5rem; border:1px solid var(--border); }
  .cn-request-label { font-size:.72rem; font-weight:700; color:var(--text-3); text-transform:uppercase; letter-spacing:.06em; margin-bottom:.35rem; }
  .cn-stop-list { display:flex; flex-wrap:wrap; gap:.4rem; }
  .cn-stop-item { font-size:.82rem; border-radius:5px; padding:.2rem .55rem; }
  .cn-stop-item.s-hard { background:#fee2e2; color:#991b1b; }
  .cn-stop-item.s-soft { background:#fef3c7; color:#92400e; }
  .cn-steps { display:flex; flex-direction:column; gap:.45rem; font-size:.87rem; }
  .cn-step { display:flex; gap:.7rem; }
  .cn-step-num { color:var(--text-3); font-weight:700; min-width:1.6rem; flex-shrink:0; }
  .cn-service { background:var(--bg); border-radius:6px; padding:.65rem .9rem; font-size:.78rem; color:var(--text-3); line-height:1.7; }

"""

css_anchor = '  /* Additional tests */'
if css_anchor not in content:
    print("ERROR: CSS anchor not found")
    exit(1)
content = content.replace(css_anchor, css_new + css_anchor, 1)
print("CSS added")

# ─── 2. REPLACE sec-consilium ─────────────────────────────────────────────
old_start = '  <!-- CONSILIUM SECTION -->\n  <div id="sec-consilium" class="sec">'
old_end   = '  <!-- /CONSILIUM SECTION -->'

start_idx = content.find(old_start)
end_idx   = content.find(old_end)
if start_idx == -1 or end_idx == -1:
    print(f"ERROR: consilium markers not found (start={start_idx}, end={end_idx})")
    exit(1)
end_idx += len(old_end)

# TODO: Replace with your actual consilium data from CLAUDE/prompts/complaints/
# This template shows the expected structure for consilium sections
new_section = '''\
  <!-- CONSILIUM SECTION -->
  <div id="sec-consilium" class="sec">
    <div class="mh-accordion">

    <!-- ===== EXAMPLE CONSILIUM ===== -->
    <details open>
      <summary>[Date] · Консилиум · [Health Concern]<span class="cn-pills"><span class="cn-pill">[N] участников</span><span class="cn-pill">Статус</span><span class="cn-pill">[N] действий</span><span class="cn-pill">[N] анализов</span></span></summary>
      <div class="mh-content">
      <!-- TODO: Fill with your consilium data from CLAUDE/prompts/complaints/ -->

      <!-- Что делать сейчас -->
      <div class="cn-section">
        <p class="cn-section-label">Что делать сейчас</p>
        <div class="cn-action-list">
          <div class="cn-action-card">
            <span class="cn-priority p-urgent">Срочно</span>
            <div class="cn-action-body">
              <div class="cn-action-title">[Intervention] <span>[Dosage/Details]</span></div>
              <div class="cn-action-note">[Reason and evidence level]</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Анализы -->
      <div class="cn-section">
        <p class="cn-section-label">Анализы — сдать в ближайшие дни</p>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Анализ</th><th>Приоритет</th><th>Зачем</th></tr></thead>
            <tbody>
              <tr><td>[Test name]</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td><td>[Reason]</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Противопоказания -->
      <div class="cn-section">
        <p class="cn-section-label">Избегать / Противопоказания</p>
        <div class="cn-stop-list">
          <span class="cn-stop-item s-hard">[Contraindication] → [Reason]</span>
        </div>
      </div>

      <!-- Шаги -->
      <div class="cn-section">
        <p class="cn-section-label">Следующие шаги</p>
        <div class="cn-steps">
          <div class="cn-step"><span class="cn-step-num">1.</span><div><strong>[Timeline]:</strong> [Action]</div></div>
          <div class="cn-step"><span class="cn-step-num">2.</span><div><strong>[Timeline]:</strong> [Action]</div></div>
        </div>
      </div>

      <!-- Исходный запрос -->
      <div class="cn-request">
        <div class="cn-request-label">Исходный запрос</div>
        <div style="font-size:.88rem;color:var(--text-2)">[Your health concern from CLAUDE/prompts/complaints/]</div>
      </div>
          <strong>Участники:</strong> Терапевт · Гастроэнтеролог · Эндокринолог · Нутрициолог · Специалист по боли · Тренер по движению · Коррелятор<br>
          <strong>Этапы:</strong> независимые мнения → синтез → дебаты → критик<br>
          <strong>Данные:</strong> 02_TABLES (все CSV) · 06_MEDICAL_HISTORY · genetics.csv<br>
          <strong>Отчёты:</strong> <code>03_AGENT_REPORTS/</code> · <code>04_ADVISOR_SUMMARY/</code>
        </div>
      </details>

      <p class="rec-disclaimer" style="margin-top:.9rem">Консилиум проведён агентами ИИ на основе медицинских данных. Не является медицинским советом. Проконсультируйтесь с врачом.</p>
      </div>
    </details>

    </div><!-- /mh-accordion -->
  </div>
  <!-- /CONSILIUM SECTION -->'''

old_block = content[start_idx:end_idx]
content = content[:start_idx] + new_section + content[end_idx:]
print(f"sec-consilium replaced: {len(old_block)} chars → {len(new_section)} chars")

with open('.//05_SITE/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done.")
