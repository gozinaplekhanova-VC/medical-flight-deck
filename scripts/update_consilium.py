#!/usr/bin/env python3
"""Redesign sec-consilium section and add new CSS classes."""

with open('./05_SITE/index.html', 'r', encoding='utf-8') as f:
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

new_section = '''\
  <!-- CONSILIUM SECTION -->
  <div id="sec-consilium" class="sec">
    <div class="mh-accordion">

    <!-- ===== КОНСИЛИУМ 2026-03-26: ДЕФИЦИТЫ ===== -->
    <details open>
      <summary>2026-03-26 · Консилиум · Дефициты и нутриенты<span class="cn-pills"><span class="cn-pill">8 участников</span><span class="cn-pill">Консенсус</span><span class="cn-pill">3 действия</span><span class="cn-pill">8 анализов</span></span></summary>
      <div class="mh-content">

      <!-- Что делать сейчас -->
      <div class="cn-section">
        <p class="cn-section-label">Что делать сейчас</p>
        <div class="cn-action-list">
          <div class="cn-action-card">
            <span class="cn-priority p-urgent">Срочно</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Магний бисглицинат <span>300–400 мг элементарного · вечером · через 2ч после омепразола</span></div>
              <div class="cn-action-note">Текущий Магнелис B6 48 мг ≈ 5 мг элементарного Mg — полностью неэффективен. Заменить. Уровень [A]. Контроль через 6–8 нед.</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-urgent">Срочно</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Витамин D3 мицеллярный <span>3000 МЕ · с обедом (жирная еда)</span> + К2 МК-7 <span>200 мкг</span></div>
              <div class="cn-action-note">Только мицеллярная/эмульгированная форма — стеаторея нарушает всасывание жирорастворимых. Не масляный раствор. Цель: 100–150 нмоль/л. [A]+[B]</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-watch">1–2 нед.</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Омега-3 EPA+DHA <span>1000 мг rTG-форма · с обедом</span></div>
              <div class="cn-action-note">Только rTG-форма (не этиловые эфиры). При хорошей ЖКТ-переносимости → до 2000 мг через 2–3 нед. [B]</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Анализы -->
      <div class="cn-section">
        <p class="cn-section-label">Анализы — сдать в ближайшие 7–10 дней</p>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Анализ</th><th>Приоритет</th><th>Зачем</th></tr></thead>
            <tbody>
              <tr><td>Витамин D 25-OH</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td><td>Базовый контроль перед дозой D3</td></tr>
              <tr><td>Магний эритроцитарный</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td><td>Сывороточный занижает внутриклеточный дефицит</td></tr>
              <tr><td>Цинк сывороточный</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td><td>LOW в 10.2024 — обновить</td></tr>
              <tr><td>Голотранскобаламин (активный B12)</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td><td>Хронический омепразол → дефицит B12 (общий B12 маскирует)</td></tr>
              <tr><td>CoQ10</td><td><span class="cn-priority p-watch" style="display:inline-flex">1–2 нед.</span></td><td>Последний 2022; Gabapentin + SOD2 AG</td></tr>
              <tr><td>Омега-3 индекс</td><td><span class="cn-priority p-watch" style="display:inline-flex">1–2 нед.</span></td><td>Никогда не измерялся</td></tr>
              <tr><td>H2/CH4 дыхательный тест (СИБР)</td><td><span class="cn-priority p-watch" style="display:inline-flex">2 нед.</span></td><td>Симптоматика: запах изо рта, вздутие → вероятный СИБР</td></tr>
              <tr><td>PCR Blastocystis</td><td><span class="cn-priority p-watch" style="display:inline-flex">2 нед.</span></td><td>3-й рецидив, актуальный статус</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Строго не применять -->
      <div class="cn-section">
        <p class="cn-section-label">Строго не применять</p>
        <div class="cn-stop-list">
          <span class="cn-stop-item s-hard">5-HTP → серотониновый синдром с эсциталопрамом</span>
          <span class="cn-stop-item s-hard">Зверобой → снижает уровень эсциталопрама (CYP2C19)</span>
          <span class="cn-stop-item s-hard">Фитоэстрогены (соя/красный клевер) → CYP19A1 + тестостерон</span>
          <span class="cn-stop-item s-hard">Берберин → CYP3A4-ингибитор, взаимодействие с эсциталопрамом</span>
          <span class="cn-stop-item s-soft">Пероральное железо → ждать лечения ЖКТ</span>
          <span class="cn-stop-item s-soft">Lactobacillus-пробиотики → до исключения СИБР</span>
        </div>
      </div>

      <!-- ТОП-5 шагов -->
      <div class="cn-section">
        <p class="cn-section-label">Следующие шаги</p>
        <div class="cn-steps">
          <div class="cn-step"><span class="cn-step-num">1.</span><div><strong>Сегодня:</strong> заменить Магнелис B6 → магний бисглицинат 300 мг вечером</div></div>
          <div class="cn-step"><span class="cn-step-num">2.</span><div><strong>3 дня:</strong> купить D3 мицеллярный 3000 МЕ + K2 MK-7 200 мкг + омега-3 rTG 1000 мг</div></div>
          <div class="cn-step"><span class="cn-step-num">3.</span><div><strong>Неделя:</strong> сдать пакет анализов (Mg эритроцитарный + Zn + D3 + CoQ10 + омега-3 индекс + голотранскобаламин B12)</div></div>
          <div class="cn-step"><span class="cn-step-num">4.</span><div><strong>2 недели:</strong> H2/CH4 дыхательный тест + PCR Blastocystis → разблокирует вопрос пробиотиков и железа</div></div>
          <div class="cn-step"><span class="cn-step-num">5.</span><div><strong>Психиатр:</strong> принести генетику CYP2C19*17 — обсудить терапевтический уровень эсциталопрама</div></div>
        </div>
      </div>

      <!-- Исходный запрос -->
      <div class="cn-request">
        <div class="cn-request-label">Исходный запрос</div>
        <div style="font-size:.88rem;color:var(--text-2)">Нутриентные дефициты на фоне хронической боли (грыжа L5-S1, Modic 1-2), омепразола, рецидивирующего Blastocystis и генетических особенностей (SOD2, CYP2C19*17). Что делать прямо сейчас?</div>
      </div>

      <!-- Служебная информация -->
      <details style="margin-top:.5rem">
        <summary style="font-size:.78rem;color:var(--text-3);padding:.5rem .7rem;cursor:pointer;list-style:none;display:flex;align-items:center;gap:.4rem">
          <span style="font-size:.9rem;color:var(--text-4)">›</span> Служебная информация
        </summary>
        <div class="cn-service" style="margin-top:.35rem">
          <strong>Участники (8 агентов):</strong> Терапевт · Гастроэнтеролог · Эндокринолог · Нутрициолог · Специалист по боли · Тренер по движению · Интегративный · Коррелятор<br>
          <strong>Этапы:</strong> независимые мнения → синтез → дебаты → критик<br>
          <strong>Данные:</strong> 02_TABLES (все CSV) · 06_MEDICAL_HISTORY · genetics.csv<br>
          <strong>Отчёты:</strong> <code>03_AGENT_REPORTS/2026-03-26_deficits_*.md</code> (8 агентов) · <code>04_ADVISOR_SUMMARY/2026-03-26_deficits_synthesis.md</code> · <code>…_debates.md</code> · <code>…_final.md</code>
        </div>
      </details>

      <p style="margin-top:.9rem;font-size:.76rem;color:var(--text-4)">Консилиум проведён агентами ИИ на основе медицинских данных. Не является медицинским советом. Проконсультируйтесь с врачом.</p>
      </div><!-- /mh-content 2026-03-26 -->
    </details>

    <!-- ===== КОНСИЛИУМ 2026-03-25: ХОЛЕСТЕРИН ===== -->
    <details>
      <summary>2026-03-25 · Консилиум · Холестерин<span class="cn-pills"><span class="cn-pill">6 участников</span><span class="cn-pill">Консенсус</span><span class="cn-pill">3 срочных</span><span class="cn-pill">6 анализов</span></span></summary>
      <div class="mh-content">

      <!-- Ключевой паттерн -->
      <div class="cn-request" style="margin-bottom:1.5rem">
        <div class="cn-request-label">Ключевой паттерн · Коррелятор</div>
        <div style="font-size:.88rem;color:var(--text-2)">24.12.2025 — холестерин <strong>5.23</strong>, ЛПНП <strong>2.76</strong> — <span style="color:#059669;font-weight:600">полная норма</span>. Через 19 дней, 12.01.2026 — ЛПНП <strong>4.29</strong> (+1.53 ммоль/л). Такая флуктуация нетипична: приоритетная задача — проверить преаналитические условия декабрьского анализа.</div>
      </div>

      <!-- Что делать -->
      <div class="cn-section">
        <p class="cn-section-label">Что делать</p>
        <div class="cn-action-list">
          <div class="cn-action-card">
            <span class="cn-priority p-urgent">Срочно</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Верифицировать декабрьский анализ</div>
              <div class="cn-action-note">Был ли натощак? Повторить липидограмму в стандартных условиях (12ч голода, без алкоголя 72ч, не после болезни)</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-urgent">Срочно</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Тестостерон <span>сдать сейчас (март 2026)</span></div>
              <div class="cn-action-note">В сент 2025 был 2.17 нмоль/л при норме 0.31–1.9. Если до сих пор повышен → основной драйвер ЛПНП. Консультация гинеколога-эндокринолога, исключить СПКЯ</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-urgent">Срочно</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Лп(а)</div>
              <div class="cn-action-note">При ЛПНП 4.29–5.39 без явной причины — обязательно исключить семейную гиперхолестеринемию. Уточнить семейный анамнез (ранний ССЗ у родственников)</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-plan">1–3 мес.</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Восстановление микробиома</div>
              <div class="cn-action-note">Тяжёлый дисбиоз (окт 2024): Bifidobacterium и Akkermansia практически = 0. Пробиотики (L. acidophilus + B. longum), псиллиум, бета-глюкан овса, ферментированные продукты</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-plan">1–3 мес.</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Витамин D + обсудить с врачом препараты</div>
              <div class="cn-action-note">D3 74.4 нмоль/л — субоптимально (июль 2025). Обсудить с врачом возможный вклад эсциталопрама и габапентина в уровень ЛПНП — не отменять самостоятельно</div>
            </div>
          </div>
          <div class="cn-action-card">
            <span class="cn-priority p-ok">Продолжать</span>
            <div class="cn-action-body">
              <div class="cn-action-title">Снижение веса</div>
              <div class="cn-action-note">В первые 3–6 мес. активного похудения ЛПНП временно растёт из-за мобилизации жира и снижения лептина. По мере стабилизации веса холестерин, как правило, снижается</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Анализы -->
      <div class="cn-section">
        <p class="cn-section-label">Что сдать</p>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>Показатель</th><th>Зачем</th><th>Приоритет</th></tr></thead>
            <tbody>
              <tr><td>Тестостерон свободный + общий</td><td>Гиперандрогения → рецепторы ЛПНП ↓ → основной драйвер</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td></tr>
              <tr><td>Лп(а)</td><td>Семейная гиперхолестеринемия — не снижается диетой</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td></tr>
              <tr><td>Липидограмма повтор (натощак)</td><td>Верифицировать: 5.23 (дек) vs 6.57 (янв) — флуктуация нетипична</td><td><span class="cn-priority p-urgent" style="display:inline-flex">Срочно</span></td></tr>
              <tr><td>25-OH-D3</td><td>Последний 74.4 нмоль/л (июль 2025) — субоптимально</td><td><span class="cn-priority p-plan" style="display:inline-flex">1 мес.</span></td></tr>
              <tr><td>CoQ10</td><td>Был снижен в 2022; дефицит нарушает утилизацию липидов</td><td><span class="cn-priority p-plan" style="display:inline-flex">1 мес.</span></td></tr>
              <tr><td>Микробиом</td><td>Тяжёлый дисбиоз окт 2024 — актуальный статус неизвестен</td><td><span class="cn-priority p-plan" style="display:inline-flex">1–2 мес.</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Детальный разбор участников -->
      <div class="cn-section">
        <p class="cn-section-label">Детальный разбор участников</p>
        <div class="mh-accordion">

          <!-- КОРРЕЛЯТОР -->
          <details>
            <summary class="rep-accent-b">Коррелятор <span class="mh-sum">динамика липидов · флуктуация дек→янв · тестостерон · лептин</span></summary>
            <div class="mh-content">
              <div class="rep-meta"><span>2026-03-25</span></div>
              <div class="rep-section">
                <h4>Полная динамика липидного профиля</h4>
                <div class="tbl-wrap">
                  <table>
                    <thead><tr><th>Дата</th><th>Хол. общ.</th><th>ЛПНП</th><th>ЛПВП</th><th>ТГ</th><th>Событие</th></tr></thead>
                    <tbody>
                      <tr><td>2023-12-23</td><td><span class="badge-ok">4.80 ✓</span></td><td>2.87 ↑</td><td>1.60</td><td>1.19</td><td>КОК принимает</td></tr>
                      <tr><td>2024-02-29</td><td><span class="badge-high">6.47 ↑</span></td><td>—</td><td>—</td><td><span class="badge-high">2.79 ↑↑</span></td><td>КОК принимает</td></tr>
                      <tr><td>2024-03-05</td><td><span class="badge-high">6.65 ↑</span></td><td>3.70 ↑</td><td>2.15</td><td>—</td><td>КОК принимает</td></tr>
                      <tr><td>2024-10-09</td><td><span class="badge-high">6.46 ↑</span></td><td>4.10 ↑</td><td>1.83</td><td>1.03</td><td>КОК принимает</td></tr>
                      <tr><td style="color:#ef4444;font-weight:600">2025-06-30</td><td colspan="4">—</td><td style="color:#ef4444;font-weight:600">ОТМЕНА КОК</td></tr>
                      <tr><td>2025-07-24</td><td><span class="badge-high">7.98 ↑↑</span></td><td><span class="badge-high">5.39 ↑↑</span></td><td>2.20</td><td>0.81</td><td>+1 мес. после отмены</td></tr>
                      <tr><td>2025-08-25</td><td><span class="badge-high">6.60 ↑</span></td><td>4.42 ↑</td><td>2.25</td><td>0.70</td><td>—</td></tr>
                      <tr><td>2025-09-07</td><td><span class="badge-high">7.65 ↑↑</span></td><td><span class="badge-high">4.96 ↑↑</span></td><td>2.08</td><td>0.68</td><td>Тест. 2.17 ↑ (гиперандрогения)</td></tr>
                      <tr><td>2025-09-20</td><td><span class="badge-high">6.85 ↑</span></td><td>—</td><td>—</td><td>—</td><td>—</td></tr>
                      <tr><td style="color:#059669;font-weight:600">2025-12-24</td><td><span class="badge-ok">5.23 ✓</span></td><td><span class="badge-ok">2.76 ✓</span></td><td>1.71</td><td>1.09</td><td style="color:#059669;font-weight:600">ПОЛНАЯ НОРМА</td></tr>
                      <tr><td>2026-01-12</td><td><span class="badge-high">6.57 ↑</span></td><td><span class="badge-high">4.29 ↑</span></td><td>1.76</td><td>1.76</td><td>+19 дней от нормы (?!)</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="rep-section">
                <h4>Ключевые корреляции</h4>
                <ul class="rep-list">
                  <li><strong>Отмена КОК (июнь 2025) → пик холестерина (июль 2025):</strong> сильная временна́я связь <span class="rep-key warn">[E]</span></li>
                  <li><strong>Тестостерон ↑ (2.17, сент 2025) ↔ ЛПНП ↑:</strong> совпадение по времени <span class="rep-key warn">[E]</span></li>
                  <li>ТГ нормализованы (0.68–0.81) при высоком ЛПНП → паттерн <strong>НЕ инсулинорезистентный</strong></li>
                  <li>вч-СРБ 0.38–0.40 мг/л → воспалительный компонент минимален</li>
                  <li>HbA1c 5.0–5.1%, HOMA-IR 2.06 → инсулинорезистентность исключена <span class="rep-key ok">[A]</span></li>
                  <li>FT4 0.80–0.83 нг/дл (март 2024) при нормальном ТТГ → паттерн Low T4 / Normal TSH</li>
                </ul>
              </div>
            </div>
          </details>

          <!-- ТЕРАПЕВТ -->
          <details>
            <summary class="rep-accent-b">Терапевт <span class="mh-sum">FH-скрининг · преаналитика · препараты</span></summary>
            <div class="mh-content">
              <div class="rep-meta"><span>2026-03-25</span></div>
              <div class="rep-section">
                <h4>Исключено</h4>
                <ul class="rep-list">
                  <li>Инсулинорезистентность / преддиабет <span class="rep-key ok">[A]</span> — HbA1c 4.9–5.1%, HOMA-IR 2.06</li>
                  <li>Гипотиреоз клинический <span class="rep-key ok">[A]</span> — ТТГ нормален на 5 измерениях</li>
                  <li>Воспалительная гиперхолестеринемия <span class="rep-key ok">[B]</span> — вч-СРБ 0.38–0.40</li>
                </ul>
              </div>
              <div class="rep-section">
                <h4>Требует исключения</h4>
                <ul class="rep-list">
                  <li><strong>Флуктуация дек→янв:</strong> +1.53 ммоль/л ЛПНП за 19 дней — нетипично. Версии: анализ 24.12 не натощак / алкоголь / разные лаборатории / острая инфекция. Повторить в стандартных условиях <span class="rep-key warn">[B]</span></li>
                  <li><strong>Семейная гиперхолестеринемия (FH):</strong> ЛПНП стабильно 3.7–5.4 — Dutch Lipid Clinic Network score. При FH диета практически не влияет. Уточнить семейный анамнез + Лп(а) <span class="rep-key ok">[A]</span></li>
                  <li><strong>Эсциталопрам 15 мг:</strong> СИОЗС ассоциированы с умеренным ростом холестерина в наблюдательных исследованиях <span class="rep-key warn">[C]</span></li>
                  <li><strong>Габапентин 900 мг:</strong> совпадение начала (дек 2025) с ростом ЛПНП в январе — слабая, проверить <span class="rep-key warn">[C]</span></li>
                </ul>
              </div>
            </div>
          </details>

          <!-- ЭНДОКРИНОЛОГ -->
          <details>
            <summary class="rep-accent-b">Эндокринолог <span class="mh-sum">КОК-отмена · гиперандрогения · Low T4 · лептин · кортизол</span></summary>
            <div class="mh-content">
              <div class="rep-meta"><span>2026-03-25</span></div>
              <div class="rep-section">
                <h4>Версия 1: Постотменный синдром КОК — наиболее вероятная <span class="rep-key warn">[B]</span></h4>
                <ul class="rep-list">
                  <li>Дроспиренон (КОК): антиандрогенный эффект → на фоне КОК холестерин <strong>4.80</strong> (дек 2023, норма)</li>
                  <li>Через 1 мес. после отмены → холестерин <strong>7.98</strong>, ЛПНП 5.39</li>
                  <li>Тестостерон сентябрь 2025: <strong>2.17 нмоль/л</strong> (норма 0.31–1.9) — гиперандрогения подтверждена</li>
                  <li>Тестостерон ↑ снижает активность рецепторов ЛПНП в печени → рост ЛПНП (механизм при СПКЯ)</li>
                  <li><strong>Нужен: тестостерон сейчас (март 2026)</strong></li>
                </ul>
              </div>
              <div class="rep-section">
                <h4>Версия 2: Low T4 при нормальном ТТГ <span class="rep-key warn">[C]</span></h4>
                <ul class="rep-list">
                  <li>Март 2024: FT4 0.80–0.83 нг/дл (норма 0.92–1.68) при нормальном ТТГ</li>
                  <li>К 2025 нормализовался (11.84 и 13.77 пмоль/л), но мониторить</li>
                </ul>
              </div>
              <div class="rep-section">
                <h4>Версия 3: Лептин ↓ при снижении веса <span class="rep-key warn">[C]</span></h4>
                <ul class="rep-list">
                  <li>Лептин 3.66 нг/мл (сент 2025, норма 4–32) — снижен</li>
                  <li>Снижение лептина → компенсаторный синтез холестерина в печени — нормальная адаптация</li>
                  <li>Поддерживает холестерин высоким даже при правильном питании, до стабилизации веса</li>
                </ul>
              </div>
            </div>
          </details>

          <!-- НУТРИЦИОЛОГ -->
          <details>
            <summary class="rep-accent-b">Нутрициолог <span class="mh-sum">дисбиоз · желчные кислоты · CoQ10 · Витамин D</span></summary>
            <div class="mh-content">
              <div class="rep-meta"><span>2026-03-25</span></div>
              <div class="rep-section">
                <h4>Ограничения диеты</h4>
                <p style="font-size:.88rem;color:var(--text-2)"><span class="rep-key ok">[A]</span> Диетическая коррекция снижает ЛПНП в среднем на 5–20%. При ЛПНП 4.29–5.39 этого недостаточно, если активны гормональные или генетические механизмы.</p>
              </div>
              <div class="rep-section">
                <h4>Дисбиоз как фактор гиперхолестеринемии <span class="rep-key warn">[B]</span></h4>
                <ul class="rep-list">
                  <li>Бифидобактерии (окт 2024): <strong>100,000 при норме ≥10⁹</strong> — в 10,000 раз ниже нормы</li>
                  <li>Лактобактерии: 100,000 при норме ≥10⁶</li>
                  <li>Akkermansia, Bifidobacterium, Lactobacillus = 0 (2016–2023, 16S-секвенирование)</li>
                  <li>Механизм: эти бактерии деконъюгируют желчные кислоты → выведение холестерина. При их отсутствии → реабсорбция → печень синтезирует новый холестерин</li>
                  <li>Вмешательство: L. acidophilus + B. longum — мета-анализы 2019–2022 подтверждают снижение ЛПНП <span class="rep-key ok">[A]</span></li>
                </ul>
              </div>
              <div class="rep-section">
                <h4>Нутриенты</h4>
                <ul class="rep-list">
                  <li>CoQ10 0.79 мкмоль/л (2022, норма 1.0–2.7) — снижен. Проверить актуальный уровень <span class="rep-key warn">[C]</span></li>
                  <li>Витамин D 74.4 нмоль/л (июль 2025, &lt;75 — субоптимально). Дефицит D ассоциирован с ↑ ЛПНП <span class="rep-key warn">[C]</span></li>
                </ul>
              </div>
            </div>
          </details>

          <!-- ИНТЕГРАТИВНЫЙ ВРАЧ -->
          <details>
            <summary class="rep-accent-b">Интегративный врач <span class="mh-sum">системная модель · ось гормоны→микробиом→печень→холестерин</span></summary>
            <div class="mh-content">
              <div class="rep-meta"><span>2026-03-25</span></div>
              <div class="rep-section">
                <h4>Многофакторная модель</h4>
                <div style="background:var(--bg-main);border-radius:6px;padding:.9rem 1rem;font-family:monospace;font-size:.82rem;color:var(--text-2);line-height:1.6;margin-bottom:.75rem">
                  Отмена КОК → тестостерон ↑ → рецепторы ЛПНП ↓ → ЛПНП ↑<br>
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+<br>
                  Дисбиоз (нет Akkermansia/Bifidobacterium) → реабсорбция желчных кислот → синтез холестерина ↑<br>
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+<br>
                  Снижение веса → лептин ↓ → адаптивный синтез холестерина ↑<br>
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+<br>
                  Возможно: FH-компонент (генетический базовый уровень ЛПНП выше нормы)
                </div>
                <p style="font-size:.88rem;color:var(--text-2)"><span class="rep-key warn">[B]</span> Совокупность этих факторов объясняет, почему «здоровое питание» даёт частичный эффект: оно работает против диетарного холестерина, но не против гормонального и микробиомного механизмов.</p>
              </div>
            </div>
          </details>

          <!-- КРИТИК -->
          <details>
            <summary class="rep-accent-b">Критик — таблица доказательности</summary>
            <div class="mh-content">
              <div class="rep-meta"><span>2026-03-25</span></div>
              <div class="tbl-wrap">
                <table>
                  <thead><tr><th>Гипотеза</th><th>Уровень</th><th>Подтверждается</th><th>Статус</th></tr></thead>
                  <tbody>
                    <tr><td>Постотменный эффект КОК / гиперандрогения</td><td><span class="rep-key warn">[B]</span></td><td>Тест. ↑ подтверждён, временна́я связь чёткая</td><td><strong>Приоритетная</strong></td></tr>
                    <tr><td>Семейная гиперхолестеринемия</td><td><span class="rep-key ok">[A]</span></td><td>ЛПНП стабильно высокий даже при КОК; семейный анамнез неизвестен</td><td><strong>Требует исключения</strong></td></tr>
                    <tr><td>Дисбиоз кишечника</td><td><span class="rep-key warn">[B]</span></td><td>Тяжёлый дисбиоз подтверждён, Akkermansia = 0</td><td>Вероятный вклад</td></tr>
                    <tr><td>Субклинический гипотиреоз (Low T4)</td><td><span class="rep-key warn">[C]</span></td><td>FT4 ↓ в 2024, ТТГ норм — неоднозначно</td><td>Слабая, мониторить</td></tr>
                    <tr><td>Влияние габапентина (с дек 2025)</td><td><span class="rep-key warn">[C]</span></td><td>Совпадение по времени с ростом в янв 2026</td><td>Слабая, проверить</td></tr>
                    <tr><td>Влияние эсциталопрама</td><td><span class="rep-key warn">[C]</span></td><td>Принимается с марта 2025, холестерин рос уже раньше</td><td>Слабая</td></tr>
                    <tr><td>Лептин ↓ при похудении</td><td><span class="rep-key warn">[C]</span></td><td>Низкий лептин подтверждён, вес снижается</td><td>Вклад вероятен</td></tr>
                    <tr><td>Диетарный вклад</td><td><span class="rep-key warn">[B]</span></td><td>Важен конкретный состав, не только «здоровое»</td><td>Не исключён</td></tr>
                  </tbody>
                </table>
              </div>
              <div class="rep-section" style="margin-top:.75rem">
                <h4>Недостаточно данных</h4>
                <ul class="rep-list">
                  <li>Лп(а) — не измерен никогда. Критически важен</li>
                  <li>Тестостерон в январе 2026 — не измерен</li>
                  <li>Декабрьский анализ — неизвестно, был ли натощак</li>
                  <li>Семейный анамнез (ССЗ у родственников) — не задокументирован</li>
                </ul>
              </div>
            </div>
          </details>

        </div><!-- /mh-accordion specialist -->
      </div>

      <!-- Исходный запрос -->
      <div class="cn-request">
        <div class="cn-request-label">Исходный запрос</div>
        <div style="font-size:.88rem;color:var(--text-2)">Стойкое повышение холестерина на фоне здорового питания и снижения веса (70→66 кг). Холестерин общий 6.57 ммоль/л, ЛПНП 4.29 ммоль/л (янв 2026) — стабильно повышены с 2024 года. ТТГ в норме, гипотиреоз исключён. Принимает эсциталопрам 15 мг, габапентин 900 мг, мелаксен 6 мг. КОК отменены в июне 2025.</div>
      </div>

      <!-- Служебная информация -->
      <details style="margin-top:.5rem">
        <summary style="font-size:.78rem;color:var(--text-3);padding:.5rem .7rem;cursor:pointer;list-style:none;display:flex;align-items:center;gap:.4rem">
          <span style="font-size:.9rem;color:var(--text-4)">›</span> Служебная информация
        </summary>
        <div class="cn-service" style="margin-top:.35rem">
          <strong>Участники (6 агентов):</strong> Коррелятор · Терапевт · Эндокринолог · Нутрициолог · Интегративный врач · Критик<br>
          <strong>Данные:</strong> blood_biochemistry, hormones, vitamins, microbiota, substances, 06_MEDICAL_HISTORY
        </div>
      </details>

      <p class="rec-disclaimer" style="margin-top:.9rem">Консилиум проведён агентами ИИ на основе медицинских данных. Не является медицинским советом. Проконсультируйтесь с врачом.</p>
      </div><!-- /mh-content 2026-03-25 -->
    </details>

    </div><!-- /mh-accordion -->
  </div>
  <!-- /CONSILIUM SECTION -->'''

old_block = content[start_idx:end_idx]
content = content[:start_idx] + new_section + content[end_idx:]
print(f"sec-consilium replaced: {len(old_block)} chars → {len(new_section)} chars")

with open('./05_SITE/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done.")
