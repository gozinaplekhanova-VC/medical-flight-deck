# Medical Flight Deck

**Local-first personal health dashboard powered by AI agents.**

A system for organizing medical documents, extracting lab data, running multi-specialist AI consultations, and visualizing everything in an interactive HTML dashboard. All data stays on your machine — no cloud, no accounts, no third-party storage.

Built to work with [Claude](https://claude.ai) desktop app (Cowork mode) or Claude Code.

> **Language:** The project is bilingual — the interface and agent prompts are in Russian, but the architecture and code are language-agnostic and can be adapted.

---

## What it does

The system takes raw medical documents (PDFs of lab results, imaging, doctor's notes) and processes them through a pipeline:

1. **Sort** — incoming files are categorized by type (blood, urine, imaging, etc.) and renamed with dates
2. **Extract** — lab values are pulled from PDFs into structured CSV tables
3. **Normalize** — units are converted to SI, reference ranges are added, status flags (normal/low/high) are set
4. **Analyze** — AI specialist agents review the data from their clinical perspective
5. **Consilium** — a multi-specialist discussion synthesizes findings and generates actionable questions for your doctor
6. **Dashboard** — everything is presented in a single-file interactive HTML dashboard

The dashboard is a standalone HTML file (~870 KB) with no external dependencies. Open it in any browser.


## Dashboard design

The dashboard is called **Medical Flight Deck** — a single `index.html` file in `05_SITE/`.

### Sections

The dashboard has 20+ sections covering laboratory data, lifestyle tracking, clinical analysis, and specialty overviews:

- **Overview** — health snapshot with status rings and key markers
- **Laboratory** — blood (CBC), biochemistry, coagulation, vitamins, hormones, urinalysis
- **Medications & Supplements** — current and past, with dosages and reasons
- **Nutrition** — meal plans displayed as collapsible accordions, food database
- **Movement** — exercise prescriptions from the movement coach agent
- **Mood** — daily mood chart from Daylio export data
- **Specialist Reports** — individual agent analyses
- **Consilium** — multi-specialist synthesis with debates and final recommendations
- **Correlations** — data-driven links between markers, mood, and symptoms
- **Medical History** — full anamnesis by specialty (cardiology, gastro, gynecology, etc.)
- **Genetics** — SNP findings, pharmacogenomics, metabolic variants
- **Questions for Doctor** — generated list of things to discuss at your next appointment

### Design system

The dashboard uses a custom color palette built around aurora lilac (`#7968B2`), mint glow (`#6FCABD`), and frost cyan (`#A1CDD2`). It supports dark mode via a toggle. Status colors follow medical conventions: green (normal), amber (warning), red (danger), dark red (critical).

No frameworks — vanilla HTML, CSS, and JavaScript. All styles and scripts are inline in the single file.

### Important rule

The file `05_SITE/index.html` is hand-edited. The legacy script `generate_dashboard.py` exists in `scripts/` but **must never be run** — it would overwrite the dashboard with an old template. All updates to the dashboard are done by directly editing `index.html`.


## How data gets into the dashboard

There are two paths for updating dashboard data:

### Path 1: Python scripts (for structured data)
Scripts in `scripts/` read CSV files from `02_TABLES/` and inject data into specific sections of `index.html`. Each script handles one section:

| Script | Dashboard section | Data source |
|--------|------------------|-------------|
| `update_overview_tab.py` | Overview | All CSVs, `overview_rules.json` |
| `update_endocrinology_tab.py` | Hormones | `hormones.csv` |
| `update_health_index.py` | Health index cards | Computed from all data |
| `update_meds.py` | Medications | `medications.csv` |
| `update_consilium.py` | Consilium | `04_ADVISOR_SUMMARY/` reports |
| `add_group_summaries.py` | Group summary cards | All lab CSVs |
| `build_timeline.py` | Timeline | All dated events → `timeline.json` |

### Path 2: Direct editing (for reports and rich content)
Agent reports, medical history, meal plans, and other narrative content are inserted directly into `index.html` by Claude during analysis sessions. This includes consilium syntheses, nutrition plans (added as `<details>` accordions), and specialist observations.

### Data flow diagram

```
00_INBOX_RAW/  (drop PDFs here)
      ↓  [sorter agent]
01_SORTED/  (organized by type and date)
      ↓  [extractor agent]
02_TABLES/  (structured CSV data)
      ↓  [normalizer agent]
02_TABLES/  (normalized units, reference ranges, status flags)
      ↓
      ├── [specialist agents] → 03_AGENT_REPORTS/
      │         ↓
      │    [consilium agent] → 04_ADVISOR_SUMMARY/
      │
      ├── [Python scripts] → 05_SITE/index.html (data sections)
      └── [Claude direct edit] → 05_SITE/index.html (reports, plans)
```


## Project structure

```
HealthDashboard/
├── 00_INBOX_RAW/           — Drop raw medical documents here
├── 01_SORTED/              — Auto-sorted by type and date
│   ├── blood/              — Blood test PDFs
│   ├── urine/              — Urinalysis PDFs
│   ├── imaging/            — MRI, ultrasound, CT, ECG
│   ├── doctors_notes/      — Consultation records
│   └── other/              — Genetics, serology, etc.
├── 02_TABLES/              — Extracted lab data (CSV + JSON config)
│   ├── blood_general.csv
│   ├── blood_biochemistry.csv
│   ├── hormones.csv
│   ├── vitamins.csv
│   ├── urine.csv
│   ├── other.csv
│   ├── genetics.csv
│   ├── medications.csv
│   ├── imaging.csv
│   ├── mood_timeline.csv
│   ├── microbiota.csv
│   ├── exercises.csv
│   ├── substances.csv
│   ├── tab_mapping.json    — Routes test names → CSV files → dashboard tabs
│   └── overview_rules.json — Dashboard display logic
├── 03_AGENT_REPORTS/       — Individual specialist analyses (Markdown)
├── 04_ADVISOR_SUMMARY/     — Consilium syntheses (synthesis → debates → final)
├── 05_SITE/
│   ├── index.html          — The dashboard (standalone, no dependencies)
│   └── timeline.json       — Event timeline data
├── 06_MEDICAL_HISTORY/     — Detailed anamnesis by specialty (Markdown)
├── 07_LIFESTYLE_DATA/      — Mood exports, supplement tracking
├── 08_NUTRITION/           — Meal planning system
│   ├── food_profile.csv    — Dish database with GI tolerance notes
│   ├── food_ingredients.csv— Ingredient inventory
│   ├── plans/              — Generated meal rotations
│   ├── requests/           — Nutrition request templates
│   └── logs/               — Progress journal
├── CLAUDE/                 — Agent definitions and prompts
│   ├── agents/             — 11 specialist agent roles
│   └── prompts/            — Workflow templates and complaint files
├── scripts/                — Python processing scripts
├── CLAUDE.md               — Main project instructions
└── requirements.txt        — Python dependencies
```


## CSV table format

All lab data CSVs follow the same schema:

| Column | Description |
|--------|-------------|
| `date` | Analysis date (YYYY-MM-DD) |
| `test_name` | Marker name |
| `value` | Numeric result |
| `unit` | Unit of measurement (SI-normalized) |
| `reference_min` | Lower bound of normal range |
| `reference_max` | Upper bound of normal range |
| `status` | `normal` / `low` / `high` / `unknown` |
| `source_file` | Original document filename |

Specialized tables (medications, imaging, mood, genetics) have their own columns — see examples in the template folder.


## Agent system

The project includes 11 AI agent roles, each with a specific clinical perspective and evidence standards:

### Workflow agents
- **Sorter** — categorizes incoming documents
- **Extractor** — pulls lab values from PDFs into CSVs
- **Normalizer** — standardizes units and adds reference ranges

### Clinical specialists
- **Therapist (conservative)** — EBM-strict, NICE/Cochrane/UpToDate references, evidence levels A–B only
- **Gastroenterologist** — Rome IV criteria, ACG guidelines
- **Endocrinologist** — Endocrine Society, ATA guidelines
- **Cardiologist** — ESC, ACC/AHA guidelines
- **Pain specialist** — biopsychosocial model, Moseley/O'Sullivan pain science

### Functional specialists
- **Movement coach** — CFT rehabilitation, functional capacity focus
- **Nutritionist** — GI-aware meal planning, integrates lab data and food tolerances

### Analytical
- **Correlator** — finds statistical associations between markers, applies Bradford Hill criteria
- **Consilium** — moderates multi-specialist discussions, synthesizes all reports

Each agent produces Markdown reports with evidence level tags: **[A]** meta-analyses, **[B]** RCTs, **[C]** case series, **[D]** theoretical, **[E]** patient experience.

### How consilium works

1. A complaint file is created in `CLAUDE/prompts/complaints/` describing current symptoms and a specific question
2. Each specialist agent analyzes the data from their perspective, focused on the complaint
3. Reports go to `03_AGENT_REPORTS/`
4. The consilium agent synthesizes everything into `04_ADVISOR_SUMMARY/` — three files per session: synthesis, debates (pro/con), and final recommendations


## Getting started

### Prerequisites
- Python 3.10+
- [Claude desktop app](https://claude.ai/download) with Cowork mode, or [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

### Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Open the project folder in Claude (Cowork mode → select folder, or `claude` in terminal)
4. Drop your medical PDFs into `00_INBOX_RAW/`
5. Ask Claude to process them — the agents will sort, extract, normalize, and analyze

### Viewing the dashboard
Open `05_SITE/index.html` in any browser. No server needed.


## Adapting for your own use

The `HealthDashboard-Template/` folder contains a clean copy of the project structure with no personal data. The dashboard has the full design with all 28 sections, onboarding instructions, dark mode, search — but all sections are empty, waiting for your data. To start fresh:

1. Copy `HealthDashboard-Template/` and rename it
2. Open `05_SITE/index.html` in your browser — you'll see the onboarding guide
3. Open Claude (Cowork → select folder, or `claude` in terminal)
4. Drop your medical PDFs into `00_INBOX_RAW/`
5. Ask Claude: *"Process files from INBOX: sort, extract, normalize, update dashboard"*
6. Refresh the browser — your data will appear in the corresponding tabs

Fill in your medical history in `06_MEDICAL_HISTORY/` and customize agent prompts in `CLAUDE/agents/` as needed.


## Using the dashboard

The dashboard has a tab-based navigation:

- **Обзор** — health snapshot with key markers and status rings
- **Анализы** — lab data (CBC, biochemistry, vitamins, hormones, urinalysis, coagulation) with time-series tables and charts
- **Образ жизни** — medications, supplements, nutrition plans, exercise, mood tracking
- **Анамнез** — medical history by specialty (cardiology, gastro, gynecology, neurology, etc.) and genetics
- **Корреляции** — data-driven connections between markers, found by the correlator agent
- **Отчёты агентов** — individual specialist analyses and consilium syntheses
- **Врачу** — generated questions and recommended tests for your next doctor visit

Status colors: green (normal), amber (warning), red (danger), dark red (critical). Use 🔍 (⌘K) for quick search across all data. Toggle dark mode with 🌙.


## Privacy

This project is designed for **local-only** use. No data is sent to cloud storage. AI processing happens through Claude's conversation interface — your medical documents are processed in the context of your Claude session.

The `.gitignore` excludes all personal data folders from version control. The template folder contains only structure and examples.


## Adding new data

1. Drop your PDF lab results into `00_INBOX_RAW/`
2. Open Claude: `cd ~/HealthDashboard && claude` (or Cowork → select folder)
3. Say: *"Process files from INBOX: sort, extract, normalize, add to tables, update dashboard"*

## Running a consilium

1. Create a complaint file in `CLAUDE/prompts/complaints/YYYY-MM-DD_topic.md`
2. Describe your symptoms, question, and context
3. Say to Claude: *"Run a consilium based on the latest complaint"*
4. Results appear in `04_ADVISOR_SUMMARY/` and can be added to the dashboard

## Warning: generate_dashboard.py

The file `scripts/generate_dashboard.py` contains a legacy HTML template. **Do not run it** — it will overwrite the dashboard with an old layout. All dashboard updates should be done by directly editing `05_SITE/index.html`. This rule is already in `CLAUDE.md`, so Claude knows it automatically.

The template folder (`HealthDashboard-Template/`) does not include this script.


## Disclaimer

> This is not a medical device or diagnostic tool. All observations, analyses, and recommendations generated by the AI agents are informational only. Always consult a qualified healthcare professional for medical decisions.


## License

MIT
