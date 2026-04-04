#!/usr/bin/env python3
"""
parse_daylio.py — Парсинг экспорта Daylio и генерация mood_timeline.csv.

Читает CSV-экспорт из приложения Daylio, нормализует оценки настроения
в числовой формат и сохраняет результат для использования в дашборде.

Использование:
    python3 scripts/parse_daylio.py [--input PATH] [--output PATH]

Примеры:
    python3 scripts/parse_daylio.py
    python3 scripts/parse_daylio.py --input 07_LIFESTYLE_DATA/daylio_export.csv
    python3 scripts/parse_daylio.py --input 07_LIFESTYLE_DATA/daylio_export.csv --output 02_TABLES/mood_timeline.csv
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


MOOD_MAP = {
    "rad": 5,
    "good": 4,
    "meh": 3,
    "bad": 2,
    "awful": 1,
}

MOOD_LABELS_RU = {
    5: "отлично",
    4: "хорошо",
    3: "нейтрально",
    2: "плохо",
    1: "ужасно",
}

DEFAULT_INPUT = "07_LIFESTYLE_DATA/daylio_export.csv"
DEFAULT_OUTPUT = "02_TABLES/mood_timeline.csv"


def normalize_mood(mood_text: str):
    """Convert mood text to numeric score (1-5). Returns None if unrecognised."""
    cleaned = mood_text.strip().lower()
    if cleaned in MOOD_MAP:
        return MOOD_MAP[cleaned]
    # Try Russian mood names as fallback
    ru_map = {
        "отлично": 5,
        "хорошо": 4,
        "нейтрально": 3,
        "средне": 3,
        "плохо": 2,
        "ужасно": 1,
    }
    if cleaned in ru_map:
        return ru_map[cleaned]
    return None


def parse_activities(activities_field: str) -> list:
    """Parse pipe-separated activities string into a list."""
    if not activities_field or not activities_field.strip():
        return []
    parts = [a.strip() for a in activities_field.split("|")]
    return [a for a in parts if a]


def parse_daylio_csv(input_path: Path) -> list:
    """Parse Daylio CSV export and return list of dicts."""
    rows = []
    with open(input_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            # Detect date column (full_date preferred, else date)
            date_val = row.get("full_date") or row.get("date") or ""
            date_val = date_val.strip()

            # Normalise date to YYYY-MM-DD if possible
            # Daylio sometimes exports as "YYYY-MM-DD" or "DD месяц" (Russian)
            if not date_val:
                print(f"  Строка {i}: пустая дата, пропускаем", file=sys.stderr)
                continue

            # Try to convert "1 ноября" → not needed since full_date is YYYY-MM-DD in our export
            # Just pass through what we have
            mood_raw = (row.get("mood") or "").strip()
            mood_score = normalize_mood(mood_raw)
            if mood_score is None:
                print(f"  Строка {i}: неизвестное настроение '{mood_raw}', пропускаем", file=sys.stderr)
                continue

            activities = parse_activities(row.get("activities") or "")

            note_title = (row.get("note_title") or "").strip()
            note_body = (row.get("note") or "").strip()
            note = note_title if note_title else note_body
            if note_title and note_body and note_title != note_body:
                note = f"{note_title}: {note_body}"

            rows.append({
                "date": date_val,
                "mood_score": mood_score,
                "mood_label": MOOD_LABELS_RU.get(mood_score, mood_raw),
                "activities": " | ".join(activities),
                "note": note,
            })

    return rows


def print_summary(rows: list) -> None:
    """Print summary statistics to stdout."""
    if not rows:
        print("Нет данных для анализа.")
        return

    total = len(rows)
    scores = [r["mood_score"] for r in rows]
    avg = sum(scores) / total

    best = max(rows, key=lambda r: r["mood_score"])
    worst = min(rows, key=lambda r: r["mood_score"])

    all_activities = []
    for r in rows:
        if r["activities"]:
            all_activities.extend([a.strip() for a in r["activities"].split("|") if a.strip()])
    activity_counts = Counter(all_activities)

    print("\n" + "=" * 50)
    print("СТАТИСТИКА DAYLIO")
    print("=" * 50)
    print(f"Всего дней:          {total}")
    print(f"Среднее настроение:  {avg:.2f} / 5.0  ({MOOD_LABELS_RU.get(round(avg), '')})")
    print(f"Лучший день:         {best['date']} — {best['mood_score']} ({best['mood_label']})")
    print(f"Худший день:         {worst['date']} — {worst['mood_score']} ({worst['mood_label']})")

    print("\nРаспределение настроения:")
    for score in range(5, 0, -1):
        count = scores.count(score)
        bar = "█" * count
        label = MOOD_LABELS_RU.get(score, str(score))
        print(f"  {score} ({label:<12}): {bar} {count}")

    if activity_counts:
        print("\nТоп-10 активностей:")
        for activity, count in activity_counts.most_common(10):
            print(f"  {activity:<20}: {count} дн.")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Парсинг экспорта Daylio → mood_timeline.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Формат входного файла (Daylio CSV):
  full_date,date,weekday,time,mood,activities,note_title,note
  Настроение: rad=5, good=4, meh=3, bad=2, awful=1
  Активности: разделены символом "|" (pipe)

Выходной файл:
  date,mood_score,mood_label,activities,note
        """
    )
    parser.add_argument(
        "--input", "-i",
        default=DEFAULT_INPUT,
        help=f"Путь к Daylio CSV-файлу (по умолчанию: {DEFAULT_INPUT})"
    )
    parser.add_argument(
        "--output", "-o",
        default=DEFAULT_OUTPUT,
        help=f"Путь для сохранения mood_timeline.csv (по умолчанию: {DEFAULT_OUTPUT})"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Ошибка: файл не найден: {input_path}", file=sys.stderr)
        print(f"Убедитесь, что файл существует и путь указан верно.", file=sys.stderr)
        sys.exit(1)

    print(f"Чтение: {input_path}")
    rows = parse_daylio_csv(input_path)

    if not rows:
        print("Ошибка: не удалось распарсить ни одной строки.", file=sys.stderr)
        sys.exit(1)

    # Sort by date ascending
    rows.sort(key=lambda r: r["date"])

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "mood_score", "mood_label", "activities", "note"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Сохранено: {output_path} ({len(rows)} строк)")

    print_summary(rows)


if __name__ == "__main__":
    main()
