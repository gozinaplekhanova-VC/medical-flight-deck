#!/usr/bin/env python3
"""Replace calcHealthIndex / updateHealthIndex / toggleHIDetail with new logic."""

with open('.//05_SITE/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD_START = 'var HI_PARAMS = ['
OLD_END   = 'document.addEventListener(\'DOMContentLoaded\', updateHealthIndex);'

si = content.find(OLD_START)
ei = content.find(OLD_END)
if si == -1 or ei == -1:
    print(f'ERROR: markers not found (start={si}, end={ei})')
    exit(1)
ei += len(OLD_END)

NEW_CODE = '''\
// ── HEALTH INDEX ─────────────────────────────────────────────────────────────
// Uses ALL keys from CHARTS. For each indicator takes the LATEST value.
// Deviation = % distance beyond the violated boundary.
// Penalties: normal=0 · border(≤10%)=1 · moderate(10–50%)=3 · severe(50–100%)=7 · critical(>100%)=15
// Clinical minimums bump certain indicators to at least "moderate" regardless of deviation.

var HI_CLINICAL_MIN = {
  // value: minimum catIdx (0=normal 1=border 2=moderate 3=severe 4=critical)
  // applied only when the indicator IS out of range
  'c_Гемоглобин':         2,
  'c_Лейкоциты':          2,
  'c_Нейтрофилы_':        2,
  'c_Нейтрофилы_абс_':    2,
  'c_Холестерин_общий':   2,
  'c_ЛПНП__LDL_':         2,
  'c_Глюкоза__натощак_':  2,
  'c_Ферритин':           2,
  'c_Витамин_B12':        2,
  'c_Витамин_D__25_OH_':  1
};

function calcHealthIndex() {
  var total = 0, penaltySum = 0;
  var cats = { normal:0, border:0, moderate:0, severe:0, critical:0 };
  var abn  = [];
  var latestDate = '';

  Object.keys(CHARTS).forEach(function(key) {
    var c = CHARTS[key];
    var pts = c.points.filter(function(p){ return p && p.y != null; });
    if (!pts.length) return;
    pts.sort(function(a,b){ return a.x < b.x ? -1 : 1; });
    var latest = pts[pts.length - 1];
    if (latest.x > latestDate) latestDate = latest.x;

    var v  = latest.y;
    var lo = (c.ref_min !== '' && c.ref_min != null) ? parseFloat(c.ref_min) : null;
    var hi = (c.ref_max !== '' && c.ref_max != null) ? parseFloat(c.ref_max) : null;
    if (lo === null && hi === null) return;  // no reference range — skip
    total++;

    // percentage deviation beyond the violated boundary
    var deviation = 0, dir = 0;
    if      (hi !== null && hi > 0 && v > hi)        { deviation = (v - hi) / hi * 100; dir =  1; }
    else if (lo !== null && lo > 0 && v < lo && v > 0){ deviation = (lo - v) / lo * 100; dir = -1; }
    else if (lo !== null && lo > 0 && v < lo && v === 0){ deviation = 100; dir = -1; }

    // map deviation → category index
    var catIdx;
    if (dir === 0)            { catIdx = 0; }  // normal
    else if (deviation <= 10) { catIdx = 1; }  // border
    else if (deviation <= 50) { catIdx = 2; }  // moderate
    else if (deviation <= 100){ catIdx = 3; }  // severe
    else                      { catIdx = 4; }  // critical

    // ALT/AST: if value >1.5× ref_max → at least severe
    if ((key === 'c_АЛТ__SGPT_' || key === 'c_АСТ__SGOT_') && hi != null && v > hi * 1.5) {
      if (catIdx < 3) catIdx = 3;
    }

    // clinical minimum override
    var minCat = HI_CLINICAL_MIN[key];
    if (minCat !== undefined && dir !== 0 && catIdx < minCat) catIdx = minCat;

    var catNames  = ['normal','border','moderate','severe','critical'];
    var penalties = [0, 1, 3, 7, 15];
    var catName   = catNames[catIdx];
    var p         = penalties[catIdx];

    penaltySum += p;
    cats[catName]++;
    if (catIdx > 0) {
      abn.push({ key:key, label:c.label, val:v, unit:c.unit,
                 date:latest.x, cat:catName, penalty:p,
                 deviation: Math.round(deviation) });
    }
  });

  var maxScore = total * 10;
  var pct = maxScore > 0 ? Math.max(0, Math.round((maxScore - penaltySum) / maxScore * 100)) : 0;

  // ── debug ───────────────────────────────────────────────────────────────────
  console.log('=== HEALTH INDEX ===');
  console.log('Indicators: ' + total +
    ' | normal=' + cats.normal + ' border=' + cats.border +
    ' moderate=' + cats.moderate + ' severe=' + cats.severe + ' critical=' + cats.critical);
  var heavy = abn.filter(function(x){ return x.cat==='severe'||x.cat==='critical'; });
  if (heavy.length) {
    console.log('Severe / Critical:');
    heavy.forEach(function(x){
      console.log('  ' + x.label + ': ' + x.val + ' ' + x.unit +
        ' [' + x.cat + ', +' + x.deviation + '%, penalty=−' + x.penalty + '] ' + x.date);
    });
  }
  console.log('max_possible=' + maxScore + '  total_penalty=' + penaltySum + '  health_index=' + pct + '%');
  // ────────────────────────────────────────────────────────────────────────────

  return { total:total, cats:cats, abn:abn, penalty:penaltySum, pct:pct, latestDate:latestDate };
}

function updateHealthIndex() {
  var r     = calcHealthIndex();
  var pct   = r.pct;
  var color = pct >= 80 ? '#22c55e' : pct >= 60 ? '#f59e0b' : pct >= 40 ? '#f97316' : '#ef4444';
  var el    = function(id){ return document.getElementById(id); };

  // Ring
  var ring = el('hi-ring');
  if (ring) {
    ring.style.background = 'conic-gradient(' + color + ' 0% ' + pct + '%, var(--border) ' + pct + '% 100%)';
    ring.style.cursor = 'pointer';
    ring.title = 'Нажмите для деталей';
    ring.onclick = function(){ toggleHIDetail(r); };
  }

  if (el('hi-pct'))  { el('hi-pct').textContent  = pct + '%'; el('hi-pct').style.color  = color; }
  if (el('hi-pct2')) { el('hi-pct2').textContent = pct + '%'; el('hi-pct2').style.color = color; }

  // Sub-line breakdown
  var c = r.cats, parts = [];
  if (c.normal)   parts.push(c.normal   + ' норм.');
  if (c.border)   parts.push(c.border   + ' погр.');
  if (c.moderate) parts.push(c.moderate + ' умер.');
  if (c.severe)   parts.push(c.severe   + ' выр.');
  if (c.critical) parts.push(c.critical + ' крит.');
  if (el('hi-sub')) el('hi-sub').textContent = parts.join(' · ');

  // Stat cards
  var critCount = (c.critical||0) + (c.severe||0);
  var modCount  = (c.moderate||0) + (c.border||0);
  if (el('hi-crit')) el('hi-crit').textContent = critCount;
  if (el('hi-imp'))  el('hi-imp').textContent  = modCount;

  var critNames = r.abn.filter(function(x){ return x.cat==='critical'||x.cat==='severe'; })
                       .map(function(x){ return x.label; }).join(', ');
  var modNames  = r.abn.filter(function(x){ return x.cat==='moderate'||x.cat==='border'; })
                       .map(function(x){ return x.label; }).join(', ');
  if (el('hi-crit-sub')) el('hi-crit-sub').textContent = critNames || '—';
  if (el('hi-imp-sub'))  el('hi-imp-sub').textContent  = modNames  || '—';

  // Latest date across all CHARTS
  var allLatest = '';
  Object.keys(CHARTS).forEach(function(k){
    CHARTS[k].points.filter(function(p){ return p && p.x; }).forEach(function(p){
      if (p.x > allLatest) allLatest = p.x;
    });
  });
  if (el('hi-lastdate')) el('hi-lastdate').textContent = allLatest || r.latestDate || '—';
  if (el('hi-lastsub'))  el('hi-lastsub').textContent  = 'по всем данным';
}

function toggleHIDetail(r) {
  var panel = document.getElementById('hi-detail-panel');
  if (panel) { panel.remove(); return; }

  var catLabel = { critical:'Критические (>100%)', severe:'Выраженные (50–100%)',
                   moderate:'Умеренные (10–50%)',  border:'Пограничные (≤10%)' };
  var catColor = { critical:'#991b1b', severe:'#ef4444', moderate:'#f97316', border:'#ca8a04' };
  var catPenalty = { critical:15, severe:7, moderate:3, border:1 };
  var cats = ['critical','severe','moderate','border'];
  var c = r.cats;

  var html = '<div id="hi-detail-panel" style="' +
    'background:var(--bg-card);border:1px solid var(--border);border-radius:10px;' +
    'padding:1rem 1.2rem;margin-top:.75rem;max-width:640px;box-shadow:0 2px 8px var(--shadow)">' +
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem">' +
    '<span style="font-size:.82rem;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.05em">Детализация индекса здоровья</span>' +
    '<button onclick="document.getElementById(\'hi-detail-panel\').remove()" ' +
    'style="background:none;border:none;cursor:pointer;color:var(--text-3);font-size:1rem">✕</button>' +
    '</div>' +
    // breakdown grid
    '<div style="display:grid;grid-template-columns:1fr auto;gap:.2rem .9rem;font-size:.83rem;margin-bottom:.75rem">' +
    '<span style="color:var(--text-2)">В норме</span><strong>' + (c.normal||0) + '</strong>' +
    '<span style="color:#ca8a04">Пограничные (≤10% от нормы)</span><strong style="color:#ca8a04">' + (c.border||0) + '</strong>' +
    '<span style="color:#f97316">Умеренные (10–50%)</span><strong style="color:#f97316">' + (c.moderate||0) + '</strong>' +
    '<span style="color:#ef4444">Выраженные (50–100%)</span><strong style="color:#ef4444">' + (c.severe||0) + '</strong>' +
    '<span style="color:#991b1b">Критические (&gt;100%)</span><strong style="color:#991b1b">' + (c.critical||0) + '</strong>' +
    '<span style="color:var(--text-3);border-top:1px solid var(--border-2);padding-top:.3rem">Всего показателей</span>' +
    '<strong style="border-top:1px solid var(--border-2);padding-top:.3rem">' + r.total + '</strong>' +
    '</div>' +
    '<div style="font-size:.74rem;color:var(--text-4);margin-bottom:.85rem">' +
    'Штрафы: погр.=−1 · умер.=−3 · выр.=−7 · крит.=−15 · ' +
    'max=' + (r.total*10) + ' · штраф=' + r.penalty + ' · итог=' + r.pct + '%</div>';

  cats.forEach(function(cat) {
    var items = r.abn.filter(function(x){ return x.cat===cat; });
    if (!items.length) return;
    html += '<div style="margin-bottom:.65rem">' +
      '<div style="font-size:.77rem;font-weight:700;color:' + catColor[cat] +
      ';margin-bottom:.3rem;text-transform:uppercase;letter-spacing:.04em">' +
      catLabel[cat] + ' (−' + catPenalty[cat] + ' за показатель)</div>';
    items.forEach(function(x){
      html += '<div style="display:flex;gap:.5rem;align-items:baseline;font-size:.83rem;padding:.15rem 0;color:var(--text-2)">' +
        '<span style="color:' + catColor[cat] + ';font-size:.6rem;line-height:1.8">●</span>' +
        '<span style="flex:1">' + x.label + '</span>' +
        '<span style="color:var(--text-2);font-weight:600">' + x.val + ' ' + x.unit + '</span>' +
        '<span style="color:var(--text-4);font-size:.75rem">+' + x.deviation + '%</span>' +
        '<span style="color:var(--text-4);font-size:.75rem">' + x.date + '</span>' +
        '</div>';
    });
    html += '</div>';
  });

  if (!r.abn.length) html += '<div style="color:#22c55e;font-size:.85rem">Все показатели в норме ✓</div>';
  html += '</div>';

  var wrap = document.querySelector('.ov-stats');
  if (wrap) wrap.insertAdjacentHTML('afterend', html);
}

document.addEventListener('DOMContentLoaded', updateHealthIndex);'''

old_block = content[si:ei]
content = content[:si] + NEW_CODE + content[ei:]
print(f'Replaced: {len(old_block)} chars → {len(NEW_CODE)} chars')

with open('.//05_SITE/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done.')
