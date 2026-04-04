#!/usr/bin/env python3
"""
build_timeline.py — Построение единой хронологии всех показателей из CSV-таблиц.

Использование:
    python3 scripts/build_timeline.py [--tables-dir PATH] [--output PATH]

Примеры:
    python3 scripts/build_timeline.py
    python3 scripts/build_timeline.py --output 05_SITE/timeline.json
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


CATEGORY_LABELS = {
    "blood_general": "Общий анализ крови",
    "blood_biochemistry": "Биохимия крови",
    "hormones": "Гормоны",
    "vitamins": "Витамины и минералы",
    "urine": "Анализ мочи",
    "other": "Прочее",
}

STATUS_PRIORITY = {"high": 2, "low": 2, "unknown": 1, "normal": 0, "text": 0}


def load_csv(csv_path: Path) -> list:
    """Загрузить CSV-файл, вернуть список словарей."""
    rows = []
    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Базовая валидация
                if not row.get("test_name") or not row.get("date"):
                    continue
                row["_source_category"] = csv_path.stem
                rows.append(row)
    except Exception as e:
        print(f"Предупреждение: не удалось прочитать {csv_path}: {e}", file=sys.stderr)
    return rows


def build_timeline(all_rows: list) -> dict:
    """Построить структуру хронологии."""
    # Группировка: test_name -> список измерений по датам
    by_test = defaultdict(list)
    for row in all_rows:
        test_name = row.get("test_name", "").strip()
        if not test_name:
            continue
        by_test[test_name].append({
            "date": row.get("date", ""),
            "value": row.get("value", ""),
            "unit": row.get("unit", ""),
            "reference_min": row.get("reference_min", ""),
            "reference_max": row.get("reference_max", ""),
            "status": row.get("status", "unknown"),
            "source_file": row.get("source_file", ""),
            "category": row.get("_source_category", "other"),
        })

    # Сортировать каждый тест по дате
    for test_name in by_test:
        by_test[test_name].sort(key=lambda x: x["date"])

    # Все уникальные даты
    all_dates = sorted(set(
        m["date"] for measurements in by_test.values()
        for m in measurements
        if m["date"]
    ))

    # Статистика по тестам
    test_stats = {}
    for test_name, measurements in by_test.items():
        statuses = [m["status"] for m in measurements]
        worst_status = max(statuses, key=lambda s: STATUS_PRIORITY.get(s, 0))
        category = measurements[-1]["category"] if measurements else "other"
        unit = measurements[-1]["unit"] if measurements else ""

        # Числовые значения для sparkline
        numeric_values = []
        for m in measurements:
            try:
                numeric_values.append(float(str(m["value"]).replace(",", ".")))
            except (ValueError, TypeError):
                pass

        test_stats[test_name] = {
            "category": category,
            "category_label": CATEGORY_LABELS.get(category, category),
            "unit": unit,
            "measurement_count": len(measurements),
            "last_date": measurements[-1]["date"] if measurements else "",
            "last_value": measurements[-1]["value"] if measurements else "",
            "last_status": measurements[-1]["status"] if measurements else "unknown",
            "worst_status": worst_status,
            "has_abnormal": worst_status in ("high", "low"),
            "numeric_values": numeric_values,
        }

    # Категории и их тесты
    categories = defaultdict(list)
    for test_name, stats in test_stats.items():
        categories[stats["category"]].append(test_name)

    return {
        "generated_at": _now_iso(),
        "all_dates": all_dates,
        "test_count": len(by_test),
        "categories": {
            cat: {
                "label": CATEGORY_LABELS.get(cat, cat),
                "tests": sorted(tests)
            }
            for cat, tests in categories.items()
        },
        "test_stats": test_stats,
        "measurements": {test: measurements for test, measurements in by_test.items()},
    }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    parser = argparse.ArgumentParser(
        description="Построение единой хронологии всех показателей из CSV-таблиц в 02_TABLES/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python3 scripts/build_timeline.py
  python3 scripts/build_timeline.py --output 05_SITE/timeline.json
        """
    )
    parser.add_argument(
        "--tables-dir", default="02_TABLES",
        help="Папка с CSV-таблицами (по умолчанию: 02_TABLES)"
    )
    parser.add_argument(
        "--output", default="05_SITE/timeline.json",
        help="Путь для сохранения timeline.json (по умолчанию: 05_SITE/timeline.json)"
    )
    args = parser.parse_args()

    tables_dir = Path(args.tables_dir)
    if not tables_dir.exists():
        print(f"Ошибка: папка {tables_dir} не найдена. Запускайте из корня проекта.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Загрузить все CSV (кроме логов)
    csv_files = [
        f for f in sorted(tables_dir.glob("*.csv"))
        if "log" not in f.name.lower()
    ]

    if not csv_files:
        print("Нет CSV-файлов в 02_TABLES/. Сначала запустите агента-извлекателя.")
        # Создать пустой timeline
        empty_timeline = {
            "generated_at": _now_iso(),
            "all_dates": [],
            "test_count": 0,
            "categories": {},
            "test_stats": {},
            "measurements": {},
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(empty_timeline, f, ensure_ascii=False, indent=2)
        print(f"Создан пустой timeline: {output_path}")
        return

    print(f"Загрузка {len(csv_files)} файлов из {tables_dir}/...")
    all_rows = []
    for csv_file in csv_files:
        rows = load_csv(csv_file)
        print(f"  {csv_file.name}: {len(rows)} строк")
        all_rows.extend(rows)

    print(f"\nВсего записей: {len(all_rows)}")

    timeline = build_timeline(all_rows)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)

    print(f"\nTimeline сохранён: {output_path}")
    print(f"  Показателей: {timeline['test_count']}")
    print(f"  Дат измерений: {len(timeline['all_dates'])}")
    print(f"  Категорий: {len(timeline['categories'])}")

    # Сводка аномалий
    abnormal = [
        name for name, stats in timeline["test_stats"].items()
        if stats["has_abnormal"]
    ]
    if abnormal:
        print(f"\nПоказатели вне нормы ({len(abnormal)}):")
        for name in sorted(abnormal):
            s = timeline["test_stats"][name]
            print(f"  {name}: {s['last_value']} {s['unit']} [{s['last_status'].upper()}]")


if __name__ == "__main__":
    main()
