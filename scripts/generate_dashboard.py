#!/usr/bin/env python3
"""
generate_dashboard.py — Генерация HTML-дашборда здоровья (чистый CSS, без Tailwind).

Использование:
    python3 scripts/generate_dashboard.py [--timeline PATH] [--output PATH]
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_timeline(path: Path) -> dict:
    if not path.exists():
        print(f"Предупреждение: timeline.json не найден: {path}", file=sys.stderr)
        return {"generated_at": "", "all_dates": [], "test_count": 0,
                "categories": {}, "test_stats": {}, "measurements": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_csv(path: Path) -> list:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def load_reports(reports_dir: Path) -> list:
    reports = []
    if not reports_dir.exists():
        return reports
    for md_file in sorted(reports_dir.glob("*.md"), reverse=True):
        content = md_file.read_text(encoding="utf-8")
        title = md_file.stem
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        date = ""
        parts = md_file.stem.split("_", 1)
        if len(parts[0]) == 10 and parts[0].count("-") == 2:
            date = parts[0]
        reports.append({"filename": md_file.name, "title": title,
                         "date": date, "content": content})
    return reports


def load_medical_history(history_dir: Path) -> list:
    files = []
    if not history_dir.exists():
        return files
    for md_file in sorted(history_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        title = md_file.stem.replace("_", " ").title()
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        files.append({"filename": md_file.name, "title": title, "content": content})
    return files


def compute_health_score(test_stats: dict) -> dict:
    stats_list = [s for s in test_stats.values()
                  if s.get("last_status") not in ("unknown", "text", None, "")]
    if not stats_list:
        return {"score": 0, "normal": 0, "total": 0}
    normal = sum(1 for s in stats_list if s.get("last_status") == "normal")
    return {"score": round(normal / len(stats_list) * 100),
            "normal": normal, "total": len(stats_list)}


def build_alerts(test_stats: dict, measurements: dict) -> list:
    alerts = []
    for name, s in test_stats.items():
        status = s.get("last_status", "")
        if status in ("high", "low"):
            ms = measurements.get(name, [])
            last = ms[-1] if ms else {}
            alerts.append({
                "name": name, "status": status,
                "value": s.get("last_value", ""), "unit": s.get("unit", ""),
                "ref_min": last.get("reference_min", ""),
                "ref_max": last.get("reference_max", ""),
                "date": s.get("last_date", ""),
                "category": s.get("category_label", ""),
            })
    alerts.sort(key=lambda a: (0 if a["status"] == "high" else 1, a["name"]))
    return alerts


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Health Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<style>
/* ── VARIABLES ───────────────────────────────── */
:root {
  --bg:        #f1f5f9;
  --bg-card:   #ffffff;
  --bg-nav:    #ffffff;
  --text:      #1e293b;
  --text-2:    #475569;
  --text-3:    #94a3b8;
  --border:    #e2e8f0;
  --accent:    #6366f1;
  --accent-h:  #4f46e5;
  --green:     #10b981;
  --green-bg:  #ecfdf5;
  --green-t:   #065f46;
  --red:       #ef4444;
  --red-bg:    #fef2f2;
  --red-t:     #991b1b;
  --blue:      #3b82f6;
  --blue-bg:   #eff6ff;
  --blue-t:    #1d4ed8;
  --amber:     #f59e0b;
  --amber-bg:  #fffbeb;
  --amber-t:   #92400e;
  --radius:    12px;
  --shadow:    0 1px 4px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.06);
}
.dark {
  --bg:        #0f172a;
  --bg-card:   #1e293b;
  --bg-nav:    #1e293b;
  --text:      #f1f5f9;
  --text-2:    #94a3b8;
  --text-3:    #64748b;
  --border:    #334155;
  --green-bg:  rgba(6,78,59,.35);
  --green-t:   #34d399;
  --red-bg:    rgba(127,29,29,.3);
  --red-t:     #f87171;
  --blue-bg:   rgba(30,58,138,.3);
  --blue-t:    #60a5fa;
  --amber-bg:  rgba(120,53,15,.3);
  --amber-t:   #fbbf24;
}

/* ── RESET ───────────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.5;
  min-height:100vh;padding:108px 0 44px;
  transition:background .2s,color .2s;
}
button{cursor:pointer;border:none;background:none;font:inherit;color:inherit}
a{color:var(--accent)}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* ── HEADER ──────────────────────────────────── */
#hdr{
  position:fixed;top:0;left:0;right:0;z-index:50;height:56px;
  background:var(--bg-nav);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 20px;gap:10px;
  box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.logo{
  width:30px;height:30px;border-radius:8px;background:var(--accent);
  color:#fff;font-weight:700;font-size:13px;display:flex;
  align-items:center;justify-content:center;flex-shrink:0;
}
.site-name{font-weight:600;font-size:14px;margin-right:auto}
@media(max-width:500px){.site-name{display:none}}
.search-box{
  position:relative;display:none;
}
@media(min-width:600px){.search-box{display:block}}
.search-box input{
  padding:5px 10px 5px 28px;font-size:13px;width:180px;
  background:var(--bg);border:1px solid var(--border);
  border-radius:8px;color:var(--text);outline:none;
  transition:border-color .15s;
}
.search-box input:focus{border-color:var(--accent)}
.search-ico{
  position:absolute;left:7px;top:50%;transform:translateY(-50%);
  color:var(--text-3);pointer-events:none;width:14px;height:14px;
}
.btn-primary{
  display:flex;align-items:center;gap:5px;padding:6px 12px;
  font-size:13px;font-weight:500;background:var(--accent);color:#fff;
  border-radius:8px;transition:background .15s;
}
.btn-primary:hover{background:var(--accent-h)}
.btn-icon{
  padding:6px;border-radius:8px;color:var(--text-2);
  display:flex;align-items:center;transition:background .15s;
}
.btn-icon:hover{background:var(--border)}
.btn-icon svg{width:16px;height:16px}

/* ── NAVBAR ──────────────────────────────────── */
#navbar{
  position:fixed;top:56px;left:0;right:0;z-index:40;
  background:var(--bg-nav);border-bottom:1px solid var(--border);
}
.nav-pills{
  max-width:1280px;margin:0 auto;
  display:flex;gap:6px;overflow-x:auto;padding:8px 20px;
  scrollbar-width:none;
}
.nav-pills::-webkit-scrollbar{display:none}
.pill{
  white-space:nowrap;padding:5px 14px;border-radius:999px;
  font-size:13px;font-weight:500;border:1px solid var(--border);
  background:var(--bg-card);color:var(--text-2);
  transition:all .15s;
}
.pill:hover{background:var(--bg);color:var(--text)}
.pill.on{background:var(--accent);color:#fff;border-color:var(--accent)}

/* ── LAYOUT ──────────────────────────────────── */
.wrap{max-width:1280px;margin:0 auto;padding:20px}
.sec{display:none}
.sec.on{display:block}
.sec-title{font-size:18px;font-weight:700;margin-bottom:18px}

/* ── CARD ────────────────────────────────────── */
.card{
  background:var(--bg-card);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px;
}
.card+.card{margin-top:14px}
.card-label{
  font-size:11px;font-weight:600;text-transform:uppercase;
  letter-spacing:.07em;color:var(--text-2);margin-bottom:12px;
}

/* ── GRID ────────────────────────────────────── */
.g5{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:18px}
@media(min-width:600px){.g5{grid-template-columns:repeat(3,1fr)}}
@media(min-width:1000px){.g5{grid-template-columns:repeat(5,1fr)}}

.g2{display:grid;grid-template-columns:1fr;gap:18px;margin-bottom:18px}
@media(min-width:900px){.g2{grid-template-columns:1fr 2fr}}

.g-tests{display:grid;grid-template-columns:1fr;gap:10px}
@media(min-width:600px){.g-tests{grid-template-columns:repeat(2,1fr)}}
@media(min-width:900px){.g-tests{grid-template-columns:repeat(3,1fr)}}
@media(min-width:1200px){.g-tests{grid-template-columns:repeat(4,1fr)}}

.g-mood{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:18px}
@media(min-width:600px){.g-mood{grid-template-columns:repeat(4,1fr)}}

/* ── STAT CARD ───────────────────────────────── */
.stat-v{font-size:24px;font-weight:700;line-height:1;margin-bottom:3px}
.stat-l{font-size:12px;color:var(--text-2)}
.c-green{color:var(--green)}
.c-red{color:var(--red)}
.c-blue{color:var(--blue)}
.c-muted{color:var(--text-2)}

/* ── GAUGE ───────────────────────────────────── */
.gauge-wrap{display:flex;flex-direction:column;align-items:center}
.gauge-desc{font-size:13px;color:var(--text-2);text-align:center;max-width:200px;margin-top:8px}

/* ── ALERTS ──────────────────────────────────── */
.alerts-scroll{display:flex;flex-direction:column;gap:6px;max-height:280px;overflow-y:auto;padding-right:2px}
.alert-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:8px 12px;border-radius:8px;border:1px solid;
  font-size:12px;cursor:pointer;transition:opacity .15s;
}
.alert-row:hover{opacity:.8}
.ah{background:var(--red-bg);border-color:rgba(239,68,68,.3);color:var(--red-t)}
.al{background:var(--blue-bg);border-color:rgba(59,130,246,.3);color:var(--blue-t)}
.a-arrow{font-size:15px;font-weight:700;margin-right:8px;flex-shrink:0}
.a-name{font-weight:600}
.a-cat{opacity:.7;font-size:11px}
.a-val{font-weight:700;text-align:right}
.a-ref{opacity:.7;font-size:11px}
.a-date{opacity:.6;font-size:10px}

/* ── BADGE ───────────────────────────────────── */
.badge{
  display:inline-flex;align-items:center;padding:2px 8px;
  border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap;
}
.b-ok{background:var(--green-bg);color:var(--green-t)}
.b-hi{background:var(--red-bg);color:var(--red-t)}
.b-lo{background:var(--blue-bg);color:var(--blue-t)}
.b-brd{background:var(--amber-bg);color:var(--amber-t)}
.b-unk{background:var(--border);color:var(--text-2)}

/* ── TEST CARD ───────────────────────────────── */
.tc{
  background:var(--bg-card);border:1px solid var(--border);
  border-radius:var(--radius);padding:14px;cursor:pointer;
  transition:box-shadow .15s,transform .15s;
}
.tc:hover{box-shadow:var(--shadow);transform:translateY(-1px)}
.tc-head{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px}
.tc-name{font-size:13px;font-weight:500;line-height:1.3;flex:1;padding-right:6px}
.tc-body{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:6px}
.tc-val{font-size:22px;font-weight:700}
.tc-unit{font-size:12px;color:var(--text-2);margin-left:3px}
.tc-chg-up{font-size:12px;font-weight:600;color:var(--red)}
.tc-chg-dn{font-size:12px;font-weight:600;color:var(--blue)}
.tc-foot{display:flex;align-items:center;justify-content:space-between}
.tc-ref{font-size:11px;color:var(--text-3)}
.tc-date{font-size:11px;color:var(--text-3)}
.tc-spark{margin-bottom:4px;opacity:.7}

/* ── TABLE ───────────────────────────────────── */
.tbl-wrap{overflow-x:auto;border-radius:var(--radius);border:1px solid var(--border)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead tr{background:var(--bg)}
th{padding:8px 12px;text-align:left;font-size:11px;font-weight:600;
   text-transform:uppercase;letter-spacing:.05em;color:var(--text-2);
   border-bottom:1px solid var(--border)}
td{padding:10px 12px;border-bottom:1px solid var(--border);color:var(--text);vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:var(--bg)}

/* ── MODAL ───────────────────────────────────── */
#modal-ov{
  display:none;position:fixed;inset:0;z-index:100;
  background:rgba(0,0,0,.5);align-items:center;justify-content:center;padding:16px;
}
#modal-ov.open{display:flex}
.modal{
  background:var(--bg-card);border-radius:16px;
  box-shadow:0 20px 60px rgba(0,0,0,.3);
  width:100%;max-width:640px;max-height:90vh;overflow-y:auto;
}
.modal-hd{
  display:flex;align-items:flex-start;justify-content:space-between;
  padding:20px 24px 14px;border-bottom:1px solid var(--border);
}
.modal-title{font-size:17px;font-weight:700}
.modal-sub{font-size:13px;color:var(--text-2);margin-top:2px}
.modal-body{padding:20px 24px}
.modal-close{
  padding:6px;border-radius:8px;color:var(--text-2);
  display:flex;align-items:center;transition:background .15s;
}
.modal-close:hover{background:var(--border)}
.modal-close svg{width:18px;height:18px}

/* ── MODAL TABLE ─────────────────────────────── */
.mtbl{width:100%;border-collapse:collapse;font-size:13px;margin-top:14px}
.mtbl th{padding:6px 10px;text-align:left;font-size:11px;font-weight:600;
         text-transform:uppercase;letter-spacing:.05em;color:var(--text-2);
         border-bottom:1px solid var(--border)}
.mtbl td{padding:8px 10px;border-bottom:1px solid var(--border);color:var(--text)}
.mtbl tr:last-child td{border-bottom:none}

/* ── TOAST ───────────────────────────────────── */
#toast{
  display:none;position:fixed;bottom:36px;left:50%;transform:translateX(-50%);
  z-index:200;background:var(--green);color:#fff;
  padding:10px 18px;border-radius:10px;font-size:13px;font-weight:500;
  align-items:center;gap:7px;box-shadow:var(--shadow);
}
#toast.show{display:flex}

/* ── DISCLAIMER ──────────────────────────────── */
#disc{
  position:fixed;bottom:0;left:0;right:0;z-index:30;
  background:var(--amber-bg);border-top:1px solid rgba(245,158,11,.3);
  padding:5px 16px;text-align:center;font-size:11px;color:var(--amber-t);
}

/* ── REPORTS ─────────────────────────────────── */
.rpt{margin-bottom:12px}
.rpt-head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:2px}
.rpt-title{font-size:15px;font-weight:700}
.rpt-fn{font-size:11px;color:var(--text-3);margin-bottom:10px}
.rpt-body{font-size:13px;color:var(--text-2);line-height:1.7}
.rpt-body h1{font-size:16px;font-weight:700;color:var(--text);margin:14px 0 5px}
.rpt-body h2{font-size:14px;font-weight:700;color:var(--text);margin:12px 0 4px}
.rpt-body h3{font-size:13px;font-weight:600;color:var(--text);margin:10px 0 3px}
.rpt-body strong{font-weight:600;color:var(--text)}
.rpt-body .bul{display:flex;gap:8px;margin:2px 0}
.btn-more{font-size:12px;color:var(--accent);cursor:pointer;margin-top:6px;background:none;border:none;padding:0}
.btn-more:hover{text-decoration:underline}
.dtag{font-size:12px;color:var(--text-3);flex-shrink:0;margin-left:10px}

/* ── ACTIVITY TAGS ───────────────────────────── */
.acts{display:flex;flex-wrap:wrap;gap:8px}
.act-tag{
  padding:4px 12px;font-size:13px;border-radius:999px;
  background:#eef2ff;color:#4338ca;
}
.dark .act-tag{background:rgba(99,102,241,.2);color:#a5b4fc}

/* ── PRINT ───────────────────────────────────── */
@media print{
  #hdr,#navbar,#modal-ov,#toast,#disc{display:none!important}
  .sec{display:block!important}
  body{padding-top:0!important}
}
</style>
</head>
<body>

<!-- HEADER -->
<header id="hdr">
  <div class="logo">H</div>
  <span class="site-name">Health Dashboard</span>
  <div class="search-box">
    <svg class="search-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input id="search-in" type="text" placeholder="Поиск показателя…" oninput="handleSearch(this.value)">
  </div>
  <button class="btn-primary" onclick="copyToClaudeClipboard()">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
    <span>Спросить Claude</span>
  </button>
  <button class="btn-icon" onclick="window.print()" title="Печать">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
  </button>
  <button class="btn-icon" onclick="toggleDark()" title="Тема">
    <svg id="ico-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    <svg id="ico-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
  </button>
</header>

<!-- NAVBAR -->
<nav id="navbar">
  <div class="nav-pills" id="nav-pills"></div>
</nav>

<!-- MAIN -->
<div class="wrap">

  <!-- OVERVIEW -->
  <div id="sec-overview" class="sec on">
    <div class="g5" id="stat-cards"></div>
    <div class="g2">
      <div class="card" style="display:flex;flex-direction:column;align-items:center">
        <div class="card-label">Индекс здоровья</div>
        <div class="gauge-wrap">
          <div id="health-gauge"></div>
          <p class="gauge-desc" id="gauge-desc"></p>
        </div>
      </div>
      <div class="card">
        <div class="card-label">Отклонения от нормы</div>
        <div class="alerts-scroll" id="alerts-list"></div>
      </div>
    </div>
    <p style="font-size:12px;color:var(--text-3)">Данные обновлены: <span id="last-update">—</span></p>
  </div>

  <!-- MEDICATIONS -->
  <div id="sec-medications" class="sec">
    <div class="sec-title">Лекарства и препараты</div>
    <div id="med-content"></div>
  </div>

  <!-- MOOD -->
  <div id="sec-mood" class="sec">
    <div class="sec-title">Настроение и самочувствие</div>
    <div id="mood-content"></div>
  </div>

  <!-- REPORTS -->
  <div id="sec-reports" class="sec">
    <div class="sec-title">Отчёты агентов</div>
    <div id="rpt-content"></div>
  </div>

  <!-- HISTORY -->
  <div id="sec-history" class="sec">
    <div class="sec-title">Медицинский анамнез</div>
    <div id="hist-content"></div>
  </div>

  <!-- DYNAMIC CATEGORY SECTIONS -->
  <div id="dyn-secs"></div>
</div>

<!-- MODAL -->
<div id="modal-ov" onclick="closeModalOverlay(event)">
  <div class="modal">
    <div class="modal-hd">
      <div>
        <div class="modal-title" id="m-title"></div>
        <div class="modal-sub" id="m-sub"></div>
      </div>
      <button class="modal-close" onclick="closeModal()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="modal-body">
      <div style="height:280px;position:relative;margin-bottom:16px"><canvas id="m-chart"></canvas></div>
      <table class="mtbl">
        <thead><tr>
          <th>Дата</th><th>Значение</th><th>Ед.</th><th>Норма</th><th>Статус</th><th>Источник</th>
        </tr></thead>
        <tbody id="m-tbody"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- TOAST -->
<div id="toast">
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
  <span id="toast-msg">Скопировано</span>
</div>

<!-- DISCLAIMER -->
<div id="disc">⚠️ Только для личного пользования. Не является медицинским советом. Проконсультируйтесь с врачом.</div>

<script>
// ── GLOBAL ERROR HANDLER (first!) ─────────────────
window.onerror = function(msg, src, line) {
  var b = document.getElementById('_eb');
  if (!b) {
    b = document.createElement('div'); b.id = '_eb';
    b.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:#dc2626;color:#fff;padding:8px 14px;font:12px monospace;white-space:pre-wrap;max-height:180px;overflow:auto';
    document.body.prepend(b);
  }
  b.textContent += msg + ' @ ' + src + ':' + line + '\\n';
  return false;
};

// ── DATA ──────────────────────────────────────────
const APP_DATA     = __DATA_JSON__;
const TIMELINE     = APP_DATA.timeline    || {};
const MEDICATIONS  = APP_DATA.medications || [];
const MOOD         = APP_DATA.mood        || [];
const SUPPLEMENTS  = APP_DATA.supplements || [];
const SUBSTANCES   = APP_DATA.substances  || [];
const REPORTS      = APP_DATA.reports     || [];
const HISTORY      = APP_DATA.history     || [];
const HEALTH_SCORE = APP_DATA.health_score || {score:0,normal:0,total:0};
const ALERTS       = APP_DATA.alerts      || [];

// ── UTILS ─────────────────────────────────────────
function esc(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function refStr(mn,mx){ if(!mn&&!mx)return '—'; if(!mn)return '<'+mx; if(!mx)return '>'+mn; return mn+'–'+mx; }
function badge(status){
  var cls={normal:'b-ok',high:'b-hi',low:'b-lo',border:'b-brd'}[status]||'b-unk';
  var lbl={normal:'Норма',high:'Высокий',low:'Низкий',border:'Граница'}[status]||'Неизв.';
  return '<span class="badge '+cls+'">'+lbl+'</span>';
}
function showToast(msg){
  var t=document.getElementById('toast');
  document.getElementById('toast-msg').textContent=msg||'Скопировано';
  t.classList.add('show');
  setTimeout(function(){t.classList.remove('show');},3000);
}
function md(text){
  return text
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/^### (.+)$/gm,'<h3>$1</h3>')
    .replace(/^## (.+)$/gm,'<h2>$1</h2>')
    .replace(/^# (.+)$/gm,'<h1>$1</h1>')
    .replace(/\\*\\*(.+?)\\*\\*/g,'<strong>$1</strong>')
    .replace(/\\*(.+?)\\*/g,'<em>$1</em>')
    .replace(/^- (.+)$/gm,'<div class="bul"><span style="color:var(--text-3)">•</span><span>$1</span></div>')
    .replace(/\\n/g,'<br>');
}

// ── DARK MODE ─────────────────────────────────────
function toggleDark(){
  var h=document.documentElement;
  var isDark=h.classList.toggle('dark');
  document.getElementById('ico-moon').style.display=isDark?'none':'block';
  document.getElementById('ico-sun').style.display=isDark?'block':'none';
  try{localStorage.setItem('hd-dark',isDark?'1':'0');}catch(e){}
}
try{
  var _s=localStorage.getItem('hd-dark');
  var _dark=_s==='1'||(_s===null&&window.matchMedia('(prefers-color-scheme:dark)').matches);
  if(_dark){
    document.documentElement.classList.add('dark');
    document.getElementById('ico-moon').style.display='none';
    document.getElementById('ico-sun').style.display='block';
  }
}catch(e){}

// ── SEARCH ────────────────────────────────────────
function handleSearch(q){
  var lq=q.toLowerCase().trim();
  document.querySelectorAll('.tc').forEach(function(c){
    c.style.display=(!lq||(c.dataset.n||'').toLowerCase().includes(lq))?'':'none';
  });
}

// ── NAVIGATION ────────────────────────────────────
var NAV=[];
function buildNav(){
  var cats=TIMELINE.categories||{};
  var icons={blood_general:'🩸',blood_biochemistry:'🧪',vitamins:'💧',urine:'🔬',other:'🧬'};
  NAV.push({id:'overview',lbl:'📊 Обзор'});
  Object.keys(cats).forEach(function(id){
    NAV.push({id:'cat-'+id,lbl:(icons[id]||'🔬')+' '+(cats[id].label||id)});
  });
  NAV.push({id:'medications',lbl:'💊 Лекарства'});
  NAV.push({id:'mood',lbl:'😊 Настроение'});
  NAV.push({id:'history',lbl:'📋 Анамнез'});
  NAV.push({id:'reports',lbl:'📝 Отчёты'});
  var c=document.getElementById('nav-pills');
  c.innerHTML=NAV.map(function(n){
    return '<button class="pill'+(n.id==='overview'?' on':'')+'" data-id="'+n.id+'" onclick="showSec(\''+n.id+'\')">'+n.lbl+'</button>';
  }).join('');
}
function showSec(id){
  document.querySelectorAll('.sec').forEach(function(s){s.classList.remove('on')});
  var el=document.getElementById('sec-'+id);
  if(el)el.classList.add('on');
  document.querySelectorAll('.pill').forEach(function(p){
    p.classList.toggle('on',p.dataset.id===id);
  });
}

// ── OVERVIEW ──────────────────────────────────────
function buildOverview(){
  var stats=TIMELINE.test_stats||{};
  var names=Object.keys(stats);
  var high=names.filter(function(n){return stats[n].last_status==='high';}).length;
  var low=names.filter(function(n){return stats[n].last_status==='low';}).length;
  var norm=names.filter(function(n){return stats[n].last_status==='normal';}).length;
  var last=(TIMELINE.all_dates||[]).slice(-1)[0]||'—';
  var cards=[
    {v:names.length,l:'Всего показателей',c:''},
    {v:norm,l:'В норме',c:'c-green'},
    {v:high,l:'Повышены',c:'c-red'},
    {v:low,l:'Понижены',c:'c-blue'},
    {v:last,l:'Последняя дата',c:'c-muted',sm:1},
  ];
  document.getElementById('stat-cards').innerHTML=cards.map(function(c){
    return '<div class="card" style="padding:14px 16px">'+
      '<div class="stat-v '+(c.c||'')+'" style="'+(c.sm?'font-size:14px':'')+'">'+esc(String(c.v))+'</div>'+
      '<div class="stat-l">'+c.l+'</div></div>';
  }).join('');

  buildGauge(HEALTH_SCORE.score);
  var s=HEALTH_SCORE.score;
  document.getElementById('gauge-desc').textContent=(
    s>=75?'Большинство показателей в норме.':
    s>=50?'Часть показателей вне нормы.':
          'Значительные отклонения.')+' ('+HEALTH_SCORE.normal+'/'+HEALTH_SCORE.total+')';

  var al=document.getElementById('alerts-list');
  if(!ALERTS.length){
    al.innerHTML='<p style="font-size:13px;color:var(--text-2)">Отклонений от нормы нет.</p>';
  } else {
    al.innerHTML=ALERTS.slice(0,20).map(function(a){
      var hi=a.status==='high';
      return '<div class="alert-row '+(hi?'ah':'al')+'" onclick="openModal(\''+esc(a.name)+'\')">'+
        '<div style="display:flex;align-items:center">'+
        '<span class="a-arrow">'+(hi?'↑':'↓')+'</span>'+
        '<div><div class="a-name">'+esc(a.name)+'</div><div class="a-cat">'+esc(a.category)+'</div></div></div>'+
        '<div style="text-align:right">'+
        '<div class="a-val">'+esc(String(a.value))+' '+esc(a.unit)+'</div>'+
        '<div class="a-ref">норма: '+refStr(a.ref_min,a.ref_max)+'</div>'+
        '<div class="a-date">'+esc(a.date)+'</div></div></div>';
    }).join('');
  }
  var genAt=TIMELINE.generated_at?new Date(TIMELINE.generated_at).toLocaleString('ru-RU'):'—';
  document.getElementById('last-update').textContent=genAt;
}

function buildGauge(score){
  var r=45,circ=2*Math.PI*r;
  var dash=(score/100)*circ;
  var col=score>=75?'#10b981':score>=50?'#f59e0b':'#ef4444';
  document.getElementById('health-gauge').innerHTML=
    '<div style="position:relative;width:130px;height:130px">'+
    '<svg width="130" height="130" viewBox="0 0 100 100" style="transform:rotate(-90deg)">'+
    '<circle cx="50" cy="50" r="45" fill="none" stroke="var(--border)" stroke-width="8"/>'+
    '<circle cx="50" cy="50" r="45" fill="none" stroke="'+col+'" stroke-width="8" '+
    'stroke-dasharray="'+dash.toFixed(1)+' '+(circ-dash).toFixed(1)+'" stroke-linecap="round"/>'+
    '</svg>'+
    '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">'+
    '<div style="font-size:26px;font-weight:700;color:'+col+'">'+score+'%</div>'+
    '</div></div>';
}

// ── CATEGORY SECTIONS ─────────────────────────────
function buildCategorySections(){
  var cats=TIMELINE.categories||{};
  var stats=TIMELINE.test_stats||{};
  var meas=TIMELINE.measurements||{};
  var container=document.getElementById('dyn-secs');
  Object.keys(cats).forEach(function(catId){
    var cat=cats[catId];
    var sec=document.createElement('div');
    sec.id='sec-cat-'+catId;
    sec.className='sec';
    var cards=(cat.tests||[]).map(function(name){
      var s=stats[name]||{};
      var ms=meas[name]||[];
      var last=ms[ms.length-1]||{};
      var prev=ms.length>=2?ms[ms.length-2]:null;
      var status=last.status||'unknown';
      var chg='';
      if(prev){
        var vN=parseFloat(last.value),vP=parseFloat(prev.value);
        if(!isNaN(vN)&&!isNaN(vP)&&vP!==0){
          var pct=(vN-vP)/vP*100;
          chg='<span class="'+(pct>0?'tc-chg-up':'tc-chg-dn')+'">'+(pct>=0?'+':'')+pct.toFixed(1)+'%</span>';
        }
      }
      var nums=(s.numeric_values||[]).filter(function(v){return isFinite(v);});
      var spark='';
      if(nums.length>=2){
        var mn=Math.min.apply(null,nums),mx=Math.max.apply(null,nums),rng=mx-mn||1;
        var W=80,H=22;
        var pts=nums.map(function(v,i){
          return ((i/(nums.length-1))*W).toFixed(1)+','+(H-((v-mn)/rng*H)).toFixed(1);
        }).join(' ');
        var lc=status==='high'?'#ef4444':status==='low'?'#3b82f6':'#10b981';
        spark='<div class="tc-spark"><svg width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">'+
          '<polyline points="'+pts+'" fill="none" stroke="'+lc+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>';
      }
      var disp=name.length>28?name.slice(0,26)+'…':name;
      return '<div class="tc" data-n="'+esc(name)+'" onclick="openModal(\''+esc(name)+'\')">'+
        '<div class="tc-head"><span class="tc-name" title="'+esc(name)+'">'+esc(disp)+'</span>'+badge(status)+'</div>'+
        '<div class="tc-body">'+
        '<div><span class="tc-val">'+esc(String(last.value||'—'))+'</span>'+
        '<span class="tc-unit">'+esc(last.unit||'')+'</span></div>'+chg+'</div>'+spark+
        '<div class="tc-foot"><span class="tc-ref">'+refStr(last.reference_min,last.reference_max)+'</span>'+
        '<span class="tc-date">'+(last.date||'')+'</span></div></div>';
    }).join('');
    sec.innerHTML='<div class="sec-title">'+esc(cat.label||catId)+'</div><div class="g-tests">'+cards+'</div>';
    container.appendChild(sec);
  });
}

// ── MEDICATIONS ───────────────────────────────────
function buildMedications(){
  var el=document.getElementById('med-content');
  if(!MEDICATIONS.length){
    el.innerHTML='<div class="card" style="text-align:center;padding:40px;color:var(--text-2)">Данных о лекарствах нет.<br><small>Добавьте данные в 02_TABLES/medications.csv</small></div>';
    return;
  }
  var rows=MEDICATIONS.map(function(m){
    return '<tr>'+
      '<td>'+esc(m.medication_name||'')+'</td>'+
      '<td>'+esc(m.dosage||'')+'</td>'+
      '<td>'+esc(m.frequency||'')+'</td>'+
      '<td>'+esc(m.date_start||'')+'</td>'+
      '<td>'+esc(m.date_end||'—')+'</td>'+
      '<td>'+esc(m.reason||'')+'</td></tr>';
  }).join('');
  el.innerHTML='<div class="tbl-wrap"><table>'+
    '<thead><tr><th>Препарат</th><th>Доза</th><th>Частота</th><th>Начало</th><th>Конец</th><th>Причина</th></tr></thead>'+
    '<tbody>'+rows+'</tbody></table></div>';
  var svg=buildMedTimeline();
  if(svg) el.innerHTML+=svg;
}

function buildMedTimeline(){
  if(!MEDICATIONS.length)return'';
  var now=new Date();
  var dates=MEDICATIONS.map(function(m){return[new Date(m.date_start),m.date_end?new Date(m.date_end):now];});
  var minD=dates.reduce(function(a,b){return a<b[0]?a:b[0];},dates[0][0]);
  var maxD=now;
  var span=maxD-minD||1;
  var W=600,H=30*MEDICATIONS.length+50,PL=140,PT=30,PB=10;
  var svg='';
  var cols=['#6366f1','#10b981','#f59e0b','#ef4444','#3b82f6','#8b5cf6'];
  MEDICATIONS.forEach(function(m,i){
    var s=new Date(m.date_start),e=m.date_end?new Date(m.date_end):now;
    var x1=PL+(s-minD)/span*(W-PL-20);
    var x2=PL+(e-minD)/span*(W-PL-20);
    var bw=Math.max(x2-x1,4);
    var y=PT+i*30;
    var col=cols[i%cols.length];
    var cur=!m.date_end||new Date(m.date_end)>now;
    svg+='<text x="'+(PL-6)+'" y="'+(y+19)+'" text-anchor="end" font-size="11" fill="var(--text-2)" font-family="sans-serif">'+esc((m.medication_name||'').slice(0,20))+'</text>';
    svg+='<rect x="'+x1.toFixed(1)+'" y="'+(y+5)+'" width="'+bw.toFixed(1)+'" height="18" rx="4" fill="'+col+'" opacity="'+(cur?'1':'0.55')+'"/>';
    if(cur) svg+='<text x="'+(x2+5).toFixed(1)+'" y="'+(y+17)+'" font-size="9" fill="'+col+'" font-family="sans-serif">сейчас</text>';
  });
  for(var i=0;i<=4;i++){
    var d=new Date(minD.getTime()+(i/4)*span);
    var x=PL+(i/4)*(W-PL-20);
    svg+='<text x="'+x.toFixed(1)+'" y="'+(PT-8)+'" text-anchor="middle" font-size="9" fill="var(--text-3)" font-family="sans-serif">'+d.toISOString().slice(0,7)+'</text>';
    svg+='<line x1="'+x.toFixed(1)+'" y1="'+PT+'" x2="'+x.toFixed(1)+'" y2="'+(H-PB)+'" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="3,3"/>';
  }
  return '<div class="card" style="margin-top:14px;overflow-x:auto">'+
    '<div class="card-label">Хронология приёма</div>'+
    '<svg width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">'+svg+'</svg></div>';
}

// ── MOOD ──────────────────────────────────────────
var moodChart=null;
function buildMood(){
  var el=document.getElementById('mood-content');
  if(!MOOD.length){
    el.innerHTML='<div class="card" style="text-align:center;padding:40px;color:var(--text-2)">Данных о настроении нет.<br><small>Запустите: python3 scripts/parse_daylio.py</small></div>';
    return;
  }
  var scores=MOOD.map(function(r){return parseFloat(r.mood_score)||0;});
  var avg=scores.reduce(function(a,b){return a+b;},0)/scores.length;
  var best=MOOD.reduce(function(a,b){return parseFloat(b.mood_score)>parseFloat(a.mood_score)?b:a;});
  var worst=MOOD.reduce(function(a,b){return parseFloat(b.mood_score)<parseFloat(a.mood_score)?b:a;});
  var actC={};
  MOOD.forEach(function(r){if(r.activities)r.activities.split('|').forEach(function(a){var t=a.trim();if(t)actC[t]=(actC[t]||0)+1;});});
  var topActs=Object.entries(actC).sort(function(a,b){return b[1]-a[1];}).slice(0,8);
  var avgCol=avg>=4?'var(--green)':avg>=3?'var(--amber)':'var(--red)';
  el.innerHTML=
    '<div class="g-mood">'+
    '<div class="card" style="padding:14px"><div class="stat-v" style="color:'+avgCol+'">'+avg.toFixed(2)+'</div><div class="stat-l">Среднее настроение</div></div>'+
    '<div class="card" style="padding:14px"><div class="stat-v">'+MOOD.length+'</div><div class="stat-l">Дней отслежено</div></div>'+
    '<div class="card" style="padding:14px"><div class="stat-v" style="font-size:14px;color:var(--green)">'+esc(best.date)+'</div><div class="stat-l">Лучший день ('+best.mood_score+')</div></div>'+
    '<div class="card" style="padding:14px"><div class="stat-v" style="font-size:14px;color:var(--red)">'+esc(worst.date)+'</div><div class="stat-l">Худший день ('+worst.mood_score+')</div></div>'+
    '</div>'+
    '<div class="card" style="margin-bottom:14px"><div class="card-label">Динамика настроения</div>'+
    '<div style="height:260px;position:relative"><canvas id="mood-chart"></canvas></div></div>'+
    (topActs.length?'<div class="card"><div class="card-label">Частые активности</div><div class="acts">'+
    topActs.map(function(a){return '<span class="act-tag">'+esc(a[0])+' <b>'+a[1]+'</b></span>';}).join('')+
    '</div></div>':'');

  requestAnimationFrame(function(){
    var ctx=document.getElementById('mood-chart');
    if(!ctx)return;
    if(moodChart){moodChart.destroy();moodChart=null;}
    var isDark=document.documentElement.classList.contains('dark');
    var gc=isDark?'rgba(255,255,255,.06)':'rgba(0,0,0,.06)';
    var tc=isDark?'#94a3b8':'#64748b';
    moodChart=new Chart(ctx,{
      type:'line',
      data:{
        labels:MOOD.map(function(r){return r.date;}),
        datasets:[{
          label:'Настроение',
          data:MOOD.map(function(r){return parseFloat(r.mood_score)||null;}),
          borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,.08)',
          tension:.35,fill:true,pointRadius:3,
          pointBackgroundColor:MOOD.map(function(r){
            var v=parseFloat(r.mood_score);
            return v>=4.5?'#10b981':v>=3.5?'#6366f1':v>=2.5?'#f59e0b':'#ef4444';
          }),
        }]
      },
      options:{
        responsive:true,maintainAspectRatio:false,
        plugins:{legend:{display:false}},
        scales:{
          x:{ticks:{color:tc,maxRotation:45,autoSkip:true,maxTicksLimit:12},grid:{color:gc}},
          y:{min:1,max:5,ticks:{color:tc,stepSize:1,callback:function(v){return({1:'ужасно',2:'плохо',3:'нейтр.',4:'хорошо',5:'отлично'})[v]||v;}},grid:{color:gc}}
        }
      }
    });
  });
}

// ── REPORTS ───────────────────────────────────────
function buildReports(){
  var el=document.getElementById('rpt-content');
  if(!REPORTS.length){
    el.innerHTML='<div class="card" style="text-align:center;padding:40px;color:var(--text-2)">Отчётов нет.</div>';
    return;
  }
  el.innerHTML=REPORTS.map(function(r,i){
    var short=r.content.slice(0,400),more=r.content.length>400;
    return '<div class="card rpt">'+
      '<div class="rpt-head"><span class="rpt-title">'+esc(r.title)+'</span><span class="dtag">'+esc(r.date)+'</span></div>'+
      '<div class="rpt-fn">'+esc(r.filename)+'</div>'+
      '<div class="rpt-body" id="rb'+i+'">'+md(short)+(more?'<span style="color:var(--text-3)">…</span>':'')+'</div>'+
      (more?'<button class="btn-more" onclick="expRpt('+i+',this)">Показать полностью ↓</button>':'')+
      '</div>';
  }).join('');
}
function expRpt(i,btn){
  document.getElementById('rb'+i).innerHTML=md(REPORTS[i].content);
  btn.remove();
}

// ── HISTORY ───────────────────────────────────────
function buildHistory(){
  var el=document.getElementById('hist-content');
  if(!HISTORY.length){
    el.innerHTML='<div class="card" style="text-align:center;padding:40px;color:var(--text-2)">Анамнез не заполнен.</div>';
    return;
  }
  el.innerHTML=HISTORY.map(function(r,i){
    var short=r.content.slice(0,300),more=r.content.length>300;
    return '<div class="card rpt">'+
      '<div class="rpt-head"><span class="rpt-title">'+esc(r.title)+'</span></div>'+
      '<div class="rpt-body" id="hb'+i+'">'+md(short)+(more?'<span style="color:var(--text-3)">…</span>':'')+'</div>'+
      (more?'<button class="btn-more" onclick="expHist('+i+',this)">Показать полностью ↓</button>':'')+
      '</div>';
  }).join('');
}
function expHist(i,btn){
  document.getElementById('hb'+i).innerHTML=md(HISTORY[i].content);
  btn.remove();
}

// ── MODAL ─────────────────────────────────────────
var detailChart=null;
function openModal(name){
  var stats=TIMELINE.test_stats||{};
  var meas=(TIMELINE.measurements||{})[name]||[];
  var s=stats[name]||{};
  document.getElementById('m-title').textContent=name;
  document.getElementById('m-sub').textContent=(s.category_label||'')+' · '+meas.length+' измерений';
  document.getElementById('m-tbody').innerHTML=meas.map(function(m){
    return '<tr>'+
      '<td>'+esc(m.date)+'</td>'+
      '<td><b>'+esc(String(m.value))+'</b></td>'+
      '<td>'+esc(m.unit||'')+'</td>'+
      '<td>'+refStr(m.reference_min,m.reference_max)+'</td>'+
      '<td>'+badge(m.status)+'</td>'+
      '<td style="color:var(--text-3);font-size:11px">'+esc(m.source_file||'')+'</td></tr>';
  }).join('');

  if(detailChart){detailChart.destroy();detailChart=null;}
  var numMs=meas.filter(function(m){return!isNaN(parseFloat(m.value));});
  var canvas=document.getElementById('m-chart');
  var isDark=document.documentElement.classList.contains('dark');
  var gc=isDark?'rgba(255,255,255,.06)':'rgba(0,0,0,.06)';
  var tc=isDark?'#94a3b8':'#64748b';
  if(numMs.length>=2){
    var last=meas[meas.length-1]||{};
    var rMin=parseFloat(last.reference_min),rMax=parseFloat(last.reference_max);
    var cols={normal:'#10b981',high:'#ef4444',low:'#3b82f6',unknown:'#94a3b8',border:'#f59e0b'};
    var datasets=[{
      label:name,
      data:numMs.map(function(m){return{x:m.date,y:parseFloat(m.value)};}),
      borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,.06)',
      tension:.3,fill:true,
      pointBackgroundColor:numMs.map(function(m){return cols[m.status]||'#94a3b8';}),
      pointRadius:5,pointHoverRadius:7,
    }];
    if(isFinite(rMin))datasets.push({label:'Мин норма',data:numMs.map(function(m){return{x:m.date,y:rMin};}),borderColor:'rgba(59,130,246,.5)',borderDash:[5,4],pointRadius:0,fill:false,tension:0});
    if(isFinite(rMax))datasets.push({label:'Макс норма',data:numMs.map(function(m){return{x:m.date,y:rMax};}),borderColor:'rgba(239,68,68,.5)',borderDash:[5,4],pointRadius:0,fill:false,tension:0});
    detailChart=new Chart(canvas,{
      type:'line',data:{datasets:datasets},
      options:{responsive:true,maintainAspectRatio:false,parsing:false,
        plugins:{legend:{labels:{color:tc,font:{size:11}}}},
        scales:{x:{type:'category',ticks:{color:tc},grid:{color:gc}},y:{ticks:{color:tc},grid:{color:gc}}}}
    });
  } else {
    var ctx2=canvas.getContext('2d');
    ctx2.clearRect(0,0,canvas.width,canvas.height);
    ctx2.fillStyle=tc;ctx2.font='13px sans-serif';ctx2.textAlign='center';
    ctx2.fillText('Недостаточно числовых данных',canvas.width/2,140);
  }
  document.getElementById('modal-ov').classList.add('open');
}
function closeModal(){
  document.getElementById('modal-ov').classList.remove('open');
  if(detailChart){detailChart.destroy();detailChart=null;}
}
function closeModalOverlay(e){if(e.target===document.getElementById('modal-ov'))closeModal();}

// ── COPY TO CLAUDE ────────────────────────────────
function copyToClaudeClipboard(){
  if(!ALERTS.length){showToast('Нет отклонений от нормы');return;}
  var lines=ALERTS.map(function(a){return'- '+a.name+': '+a.value+' '+a.unit+' (норма: '+refStr(a.ref_min,a.ref_max)+', статус: '+a.status+')';}).join('\\n');
  var text='Здравствуйте! Прошу помочь интерпретировать результаты анализов.\\n\\nОтклонения от нормы:\\n'+lines+'\\n\\nПодскажите, что это может означать и на что обратить внимание?';
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(function(){showToast('Скопировано в буфер обмена');});
  } else {
    var ta=document.createElement('textarea');ta.value=text;
    ta.style.cssText='position:fixed;opacity:0';
    document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);
    showToast('Скопировано в буфер обмена');
  }
}

// ── BOOT ──────────────────────────────────────────
buildNav();
buildOverview();
buildCategorySections();
buildMedications();
buildMood();
buildReports();
buildHistory();
try{lucide.createIcons();}catch(e){}
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Генерация HTML-дашборда здоровья.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--timeline", default="05_SITE/timeline.json")
    parser.add_argument("--output",   default="05_SITE/index.html")
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    timeline_path    = base / args.timeline
    output_path      = base / args.output
    medications_path = base / "02_TABLES"         / "medications.csv"
    mood_path        = base / "02_TABLES"         / "mood_timeline.csv"
    supplements_path = base / "07_LIFESTYLE_DATA" / "supplements.csv"
    substances_path  = base / "07_LIFESTYLE_DATA" / "substances.csv"
    reports_dir      = base / "03_AGENT_REPORTS"
    history_dir      = base / "06_MEDICAL_HISTORY"

    print("Загрузка данных...")
    timeline    = load_timeline(timeline_path)
    medications = load_csv(medications_path)
    mood        = load_csv(mood_path)
    supplements = load_csv(supplements_path)
    substances  = load_csv(substances_path)
    reports     = load_reports(reports_dir)
    history     = load_medical_history(history_dir)

    print(f"  Показателей:      {timeline.get('test_count', 0)}")
    print(f"  Лекарств:         {len(medications)}")
    print(f"  Настроение:       {len(mood)} дней")
    print(f"  Отчётов:          {len(reports)}")
    print(f"  Анамнез (файлов): {len(history)}")

    health_score = compute_health_score(timeline.get("test_stats", {}))
    alerts       = build_alerts(
        timeline.get("test_stats", {}),
        timeline.get("measurements", {})
    )

    print(f"  Индекс здоровья:  {health_score['score']}% "
          f"({health_score['normal']}/{health_score['total']} в норме)")
    print(f"  Отклонений:       {len(alerts)}")

    app_data = {
        "timeline":     timeline,
        "medications":  medications,
        "mood":         mood,
        "supplements":  supplements,
        "substances":   substances,
        "reports":      reports,
        "history":      history,
        "health_score": health_score,
        "alerts":       alerts,
    }

    data_json = json.dumps(app_data, ensure_ascii=False)
    data_json = data_json.replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    size_kb = output_path.stat().st_size // 1024
    print(f"\nДашборд сохранён: {output_path} ({size_kb} KB)")
    print(f"Открыть: open {output_path}")


if __name__ == "__main__":
    main()
