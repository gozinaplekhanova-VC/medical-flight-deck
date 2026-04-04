#!/usr/bin/env python3
"""Replace sec-meds section based on medications.csv."""

with open('./05_SITE/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD_START = '  <div id="sec-meds" class="sec">'
OLD_END   = '\n  <div id="sec-supp" class="sec">'

si = content.find(OLD_START)
ei = content.find(OLD_END)
if si == -1 or ei == -1:
    print(f'ERROR: markers not found (start={si}, end={ei})')
    exit(1)

NEW_MEDS = '''\
  <div id="sec-meds" class="sec">
    <p class="section-title">Лекарства и препараты</p>

    <!-- Принимается сейчас -->
    <div style="margin-bottom:1.5rem">
      <p style="font-size:.8rem;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem">Принимается сейчас</p>
      <div style="display:flex;flex-wrap:wrap;gap:.75rem">

        <div style="background:var(--bg-card);border-radius:8px;padding:1rem 1.25rem;box-shadow:0 1px 3px var(--shadow);border-left:3px solid #10b981;flex:1;min-width:220px">
          <div style="font-weight:600;color:var(--text)">Эсциталопрам</div>
          <div style="font-size:.85rem;color:var(--text-2)">15 мг/день · 1×/день утром</div>
          <div style="font-size:.8rem;color:var(--text-3);margin-top:.2rem">с 01.10.2025</div>
          <div style="font-size:.83rem;color:var(--text-2);margin-top:.5rem"><b>Причина:</b> снижение сенситизации нервной системы, тревожность</div>
          <div style="font-size:.8rem;color:var(--text-3);margin-top:.2rem">С марта 2025 — 10 мг, с октября 2025 — 15 мг</div>
        </div>

        <div style="background:var(--bg-card);border-radius:8px;padding:1rem 1.25rem;box-shadow:0 1px 3px var(--shadow);border-left:3px solid #10b981;flex:1;min-width:220px">
          <div style="font-weight:600;color:var(--text)">Габапентин</div>
          <div style="font-size:.85rem;color:var(--text-2)">900 мг · на ночь</div>
          <div style="font-size:.8rem;color:var(--text-3);margin-top:.2rem">с 01.12.2025</div>
          <div style="font-size:.83rem;color:var(--text-2);margin-top:.5rem"><b>Причина:</b> сон, хроническая боль</div>
        </div>

        <div style="background:var(--bg-card);border-radius:8px;padding:1rem 1.25rem;box-shadow:0 1px 3px var(--shadow);border-left:3px solid #10b981;flex:1;min-width:220px">
          <div style="font-weight:600;color:var(--text)">Мелатонин</div>
          <div style="font-size:.85rem;color:var(--text-2)">3–6 мг · на ночь</div>
          <div style="font-size:.8rem;color:var(--text-3);margin-top:.2rem">с 2021</div>
          <div style="font-size:.83rem;color:var(--text-2);margin-top:.5rem"><b>Причина:</b> трудности с засыпанием</div>
        </div>

      </div>
    </div>

    <!-- По необходимости -->
    <div style="margin-bottom:1.5rem">
      <p style="font-size:.8rem;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem">По необходимости (PRN)</p>
      <div style="display:flex;flex-wrap:wrap;gap:.5rem">
        <div style="background:var(--bg-card);border-radius:8px;padding:.75rem 1rem;box-shadow:0 1px 3px var(--shadow);border-left:3px solid #94a3b8">
          <div style="font-weight:600;font-size:.9rem;color:var(--text)">Монурал 1 пакет</div>
          <div style="font-size:.8rem;color:var(--text-3)">Обострение цистита</div>
        </div>
        <div style="background:var(--bg-card);border-radius:8px;padding:.75rem 1rem;box-shadow:0 1px 3px var(--shadow);border-left:3px solid #94a3b8">
          <div style="font-weight:600;font-size:.9rem;color:var(--text)">Антацид (Al + Mg гидроксид)</div>
          <div style="font-size:.8rem;color:var(--text-3)">Изжога / желчный рефлюкс</div>
        </div>
      </div>
    </div>

    <!-- История -->
    <p style="font-size:.8rem;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em;margin-bottom:.6rem">История (завершённые курсы)</p>
    <div class="tbl-wrap">
      <table>
        <thead><tr>
          <th>Препарат</th><th>Доза / частота</th><th>Период</th><th>Назначил</th><th>Причина</th><th>Примечания</th>
        </tr></thead>
        <tbody>
        <tr>
          <td style="font-weight:500;color:var(--text)">Эсциталопрам 10 мг</td>
          <td class="unit">10 мг/день · 1×/день</td>
          <td class="norm" style="white-space:nowrap">01.03.2025 – 16.02.2026</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Тревожность / аффективная дестабилизация</td>
          <td style="font-size:.8rem;color:var(--text-3)">С октября 2025 доза повышена до 15 мг</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Мелоксикам</td>
          <td class="unit">—</td>
          <td class="norm" style="white-space:nowrap">01.12.2025 – 31.12.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Боль / воспаление</td>
          <td style="font-size:.8rem;color:var(--text-3)">Без реакции желчным рефлюксом</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Телфаст (Фексофенадин)</td>
          <td class="unit">180 мг</td>
          <td class="norm" style="white-space:nowrap">01.01.2024 – 31.12.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Аллергия</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Оксикарбазепин</td>
          <td class="unit">150 мг/день → 450 мг/день</td>
          <td class="norm" style="white-space:nowrap">01.01.2025 – 30.09.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Стабилизация состояния</td>
          <td style="font-size:.8rem;color:var(--text-3)">Янв–мар: 150 мг; с 01.03: 300 мг утром + 150 мг вечером</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Фенибут</td>
          <td class="unit">150–500 мг · ежедневно</td>
          <td class="norm" style="white-space:nowrap">01.09.2024 – 31.07.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Нарушение сна</td>
          <td style="font-size:.8rem;color:var(--text-3)">Очень хорошо влиял на сон</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Золпидем</td>
          <td class="unit">1 мг · иногда</td>
          <td class="norm" style="white-space:nowrap">01.06.2025 – 31.07.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Бессонница</td>
          <td style="font-size:.8rem;color:var(--text-3)">Плохое самочувствие с утра</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">КОК (Дроспиренон + ЭЭ)</td>
          <td class="unit">ежедневно</td>
          <td class="norm" style="white-space:nowrap">2021 – 30.06.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Контрацепция</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Этифоксин</td>
          <td class="unit">50 мг · по необходимости</td>
          <td class="norm" style="white-space:nowrap">01.09.2024 – 30.06.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Сильная тревога</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Домперидон</td>
          <td class="unit">10 мг</td>
          <td class="norm" style="white-space:nowrap">01.06.2025 – 01.07.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Тошнота / моторика ЖКТ</td>
          <td style="font-size:.8rem;color:var(--text-3)">Даты приблизительные</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Омепразол</td>
          <td class="unit">20 мг</td>
          <td class="norm" style="white-space:nowrap">01.04.2025 – 30.04.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Защита желудка / рефлюкс</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Целекоксиб</td>
          <td class="unit">400 мг</td>
          <td class="norm" style="white-space:nowrap">01.04.2025 – 15.04.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Боль / воспаление</td>
          <td style="font-size:.8rem;color:var(--text-3)">Реакция желчным рефлюксом</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Агомелатин</td>
          <td class="unit">25 мг · на ночь</td>
          <td class="norm" style="white-space:nowrap">01.10.2024 – 01.03.2025</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">—</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Кветиапин</td>
          <td class="unit">25–60 мг</td>
          <td class="norm" style="white-space:nowrap">01.01.2024 – 29.02.2024; 01.12.2024 – 31.12.2024</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Тревожность / аффективная дестабилизация</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Эсциталопрам 10 мг</td>
          <td class="unit">10 мг/день · 1×/день</td>
          <td class="norm" style="white-space:nowrap">01.09.2024 – 24.11.2024</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">Тревожность / аффективная дестабилизация после ПАВ</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Омега-3 (Омакор)</td>
          <td class="unit">1000 мг · 2×/день</td>
          <td class="norm" style="white-space:nowrap">10.03.2024 – 10.06.2024</td>
          <td class="unit">кардиолог</td>
          <td style="font-size:.83rem;color:var(--text-2)">Повышенный холестерин и ЛПНП</td>
          <td style="font-size:.8rem;color:var(--text-3)">На фоне диетической коррекции</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Амитриптилин</td>
          <td class="unit">25 мг/день</td>
          <td class="norm" style="white-space:nowrap">15.02.2024 – 01.03.2024</td>
          <td class="unit">—</td>
          <td style="font-size:.83rem;color:var(--text-2)">—</td>
          <td class="unit">—</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Нимесулид</td>
          <td class="unit">100 мг · 2×/день</td>
          <td class="norm" style="white-space:nowrap">20.01.2024 – 03.02.2024</td>
          <td class="unit">невролог</td>
          <td style="font-size:.83rem;color:var(--text-2)">Обострение болей в пояснице</td>
          <td style="font-size:.8rem;color:var(--text-3)">Не более 15 дней; с омепразолом</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Витамин D3 (Аквадетрим)</td>
          <td class="unit">2000 МЕ · 1×/день</td>
          <td class="norm" style="white-space:nowrap">01.02.2023 – 31.07.2023</td>
          <td class="unit">терапевт</td>
          <td style="font-size:.83rem;color:var(--text-2)">Дефицит витамина D</td>
          <td style="font-size:.8rem;color:var(--text-3)">Контроль 25-OH-D3 через 3 месяца</td>
        </tr>
        <tr>
          <td style="font-weight:500;color:var(--text)">Сорбифер Дурулес</td>
          <td class="unit">100 мг · 1×/день</td>
          <td class="norm" style="white-space:nowrap">15.12.2022 – 15.03.2023</td>
          <td class="unit">терапевт</td>
          <td style="font-size:.83rem;color:var(--text-2)">Дефицит железа / ферритин 22 мкг/л</td>
          <td style="font-size:.8rem;color:var(--text-3)">Между едой; без молока и чая</td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>

'''

old_block = content[si:ei]
content = content[:si] + NEW_MEDS + content[ei:]
print(f'sec-meds replaced: {len(old_block)} chars → {len(NEW_MEDS)} chars')

with open('./05_SITE/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done.')
