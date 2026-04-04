#!/usr/bin/env python3
"""
normalize_values.py — Нормализация единиц измерения и заполнение референсных значений.

Использование:
    python3 scripts/normalize_values.py [--file CSV_PATH] [--all] [--dry-run]

Примеры:
    python3 scripts/normalize_values.py --all
    python3 scripts/normalize_values.py --file 02_TABLES/blood_biochemistry.csv
    python3 scripts/normalize_values.py --all --dry-run  # показать изменения без записи
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path


# Таблица конверсии единиц — список, чтобы избежать коллизий дублирующихся ключей.
# Каждый элемент: (from_units, to_unit, factor, test_keywords)
# from_units — список синонимов исходной единицы (рус + англ варианты)
UNIT_CONVERSIONS = [
    # Глюкоза: mg/dL → ммоль/л
    (["мг/дл", "mg/dl"], "ммоль/л", 0.0555,
     ["глюкоза", "glucose", "сахар крови", "fasting glucose"]),

    # Холестерин и липиды: mg/dL → ммоль/л
    (["мг/дл", "mg/dl"], "ммоль/л", 0.02586,
     ["холестерин", "cholesterol", "лпнп", "лпвп", "ldl", "hdl",
      "триглицериды", "triglyceride"]),

    # Креатинин: mg/dL → мкмоль/л
    (["мг/дл", "mg/dl"], "мкмоль/л", 88.42,
     ["креатинин", "creatinine"]),

    # Мочевая кислота: mg/dL → мкмоль/л
    (["мг/дл", "mg/dl"], "мкмоль/л", 59.48,
     ["мочевая кислота", "uric acid", "урат"]),

    # Мочевина: mg/dL → ммоль/л
    (["мг/дл", "mg/dl"], "ммоль/л", 0.357,
     ["мочевина", "urea"]),

    # Мочевина азот (BUN): mg/dL → ммоль/л
    (["мг/дл", "mg/dl"], "ммоль/л", 0.357,
     ["bun", "мочевина азот"]),

    # Кальций: mg/dL → ммоль/л
    (["мг/дл", "mg/dl"], "ммоль/л", 0.2495,
     ["кальций", "calcium"]),

    # Магний: mg/dL → ммоль/л
    (["мг/дл", "mg/dl"], "ммоль/л", 0.4114,
     ["магний", "magnesium"]),

    # Железо: µg/dL, ug/dL → мкмоль/л
    (["мкг/дл", "µg/dl", "ug/dl"], "мкмоль/л", 0.1791,
     ["железо", "iron", "железо (сыворотка)", "serum iron"]),

    # Билирубин: mg/dL → мкмоль/л
    (["мг/дл", "mg/dl"], "мкмоль/л", 17.1,
     ["билирубин", "bilirubin"]),

    # Белок общий (кровь): g/dL → г/л
    (["г/дл", "g/dl"], "г/л", 10.0,
     ["белок общий", "total protein", "альбумин", "albumin",
      "глобулин", "globulin"]),

    # Гемоглобин: g/dL → г/л
    (["г/дл", "g/dl"], "г/л", 10.0,
     ["гемоглобин", "hemoglobin", "haemoglobin"]),

    # MCHC: g/dL → г/л
    (["г/дл", "g/dl"], "г/л", 10.0,
     ["mchc", "средняя концентрация гемоглобина"]),

    # Витамин D: ng/mL → нмоль/л
    (["нг/мл", "ng/ml"], "нмоль/л", 2.496,
     ["витамин d", "vitamin d", "25-oh", "25(oh)d", "кальцидиол"]),

    # Витамин B12: pg/mL → пмоль/л
    (["пг/мл", "pg/ml"], "пмоль/л", 0.738,
     ["витамин b12", "vitamin b12", "b12", "кобаламин", "cobalamin"]),

    # Ферритин: ng/mL → нг/мл (уже правильная единица, конверсия не нужна)

    # Фолиевая кислота: ng/mL → нмоль/л
    (["нг/мл", "ng/ml"], "нмоль/л", 2.265,
     ["фолиевая", "folate", "фолат"]),

    # Кортизол: мкг/дл, µg/dL → нмоль/л
    (["мкг/дл", "µg/dl", "ug/dl"], "нмоль/л", 27.59,
     ["кортизол", "cortisol"]),

    # Т4 свободный: нг/дл, ng/dL → пмоль/л
    (["нг/дл", "ng/dl"], "пмоль/л", 12.87,
     ["т4 свободный", "т4", "t4", "тироксин"]),

    # Т3 свободный: пг/мл, pg/mL → пмоль/л
    (["пг/мл", "pg/ml"], "пмоль/л", 1.536,
     ["т3 свободный", "т3", "t3", "трийодтиронин"]),
]

# Показатели мочи — НЕ применять референсы из крови
URINE_ONLY_TESTS = {
    "белок (моча)", "глюкоза (моча)", "лейкоциты (осадок)",
    "эритроциты (осадок)", "уробилиноген", "билирубин (моча)",
    "кетоны (моча)", "нитриты (моча)", "кровь (моча)",
    "цилиндры (моча)", "бактерии (моча)", "дрожжи (моча)",
    "лейкоцитарная эстераза", "посев мочи (культура)",
    "цвет мочи", "прозрачность мочи",
}

# Референсные значения: test_name -> (min, max, unit, notes)
# Для женщин взрослых (общие значения)
REFERENCE_VALUES = {
    # ОАК
    "гемоглобин": (120, 160, "г/л", "женщины"),
    "эритроциты": (3.8, 5.1, "10^12/л", ""),
    "лейкоциты": (4.0, 9.0, "10^9/л", ""),
    "тромбоциты": (150, 400, "10^9/л", ""),
    "сое": (2, 20, "мм/ч", "женщины"),
    "соэ": (2, 20, "мм/ч", "женщины"),
    "гематокрит": (36, 46, "%", "женщины"),
    "нейтрофилы": (47, 72, "%", "относительное содержание"),
    "лимфоциты": (19, 37, "%", ""),
    "моноциты": (3, 11, "%", ""),
    "эозинофилы": (0.5, 5, "%", ""),
    "базофилы": (0, 1, "%", ""),

    # Биохимия
    "глюкоза": (3.9, 5.6, "ммоль/л", "натощак"),
    "общий белок": (64, 83, "г/л", ""),
    "белок": (64, 83, "г/л", ""),
    "альбумин": (35, 52, "г/л", ""),
    "креатинин": (44, 97, "мкмоль/л", "женщины"),
    "мочевина": (2.5, 6.4, "ммоль/л", ""),
    "алт": (0, 35, "Ед/л", "женщины"),
    "аст": (0, 31, "Ед/л", "женщины"),
    "ггтп": (0, 38, "Ед/л", "женщины"),
    "щелочная фосфатаза": (35, 105, "Ед/л", ""),
    "щф": (35, 105, "Ед/л", ""),
    "билирубин общий": (3.4, 17.1, "мкмоль/л", ""),
    "билирубин прямой": (0, 5.1, "мкмоль/л", ""),
    "билирубин непрямой": (0, 13.6, "мкмоль/л", ""),
    "холестерин": (0, 5.2, "ммоль/л", "целевое <5.2"),
    "холестерин общий": (0, 5.2, "ммоль/л", ""),
    "лпнп": (0, 3.0, "ммоль/л", "целевое <3.0"),
    "лпвп": (1.0, 2.7, "ммоль/л", "желательно >1.2"),
    "триглицериды": (0, 1.7, "ммоль/л", ""),
    "срб": (0, 5.0, "мг/л", ""),
    "с-реактивный белок": (0, 5.0, "мг/л", ""),
    "мочевая кислота": (0, 360, "мкмоль/л", "женщины"),
    "кальций": (2.15, 2.55, "ммоль/л", ""),
    "фосфор": (0.87, 1.45, "ммоль/л", ""),
    "натрий": (136, 145, "ммоль/л", ""),
    "калий": (3.5, 5.1, "ммоль/л", ""),
    "хлор": (98, 107, "ммоль/л", ""),
    "магний": (0.66, 1.05, "ммоль/л", ""),
    "железо": (9.0, 30.0, "мкмоль/л", "женщины"),

    # Гормоны
    "ттг": (0.4, 4.0, "мЕД/л", ""),
    "т4 свободный": (9.0, 19.0, "пмоль/л", ""),
    "т3 свободный": (2.6, 5.7, "пмоль/л", ""),
    "кортизол": (138, 690, "нмоль/л", "утром 8-10ч"),
    "дгэа-с": (1.65, 9.15, "мкмоль/л", "женщины 25-34 лет"),
    "инсулин": (3, 25, "мЕД/л", "натощак"),

    # Витамины
    "витамин d": (75, 250, "нмоль/л", "оптимум 100-150"),
    "25-oh витамин d": (75, 250, "нмоль/л", ""),
    "витамин b12": (148, 740, "пмоль/л", ""),
    "b12": (148, 740, "пмоль/л", ""),
    "ферритин": (15, 150, "нг/мл", "оптимум >50"),
    "фолиевая кислота": (7.0, 45.0, "нмоль/л", ""),
    "фолат": (7.0, 45.0, "нмоль/л", ""),
}


def find_unit_conversion(test_name: str, from_unit: str) -> tuple:
    """Найти конверсию для показателя. Возвращает (to_unit, factor) или (None, None)."""
    test_lower = test_name.lower().strip()
    from_lower = from_unit.lower().strip()

    for (from_units, to_unit, factor, test_keywords) in UNIT_CONVERSIONS:
        # Проверить совпадение единицы (любой из синонимов)
        if from_lower not in [u.lower() for u in from_units]:
            continue
        # Если целевая единица совпадает с исходной — пропустить (уже нормализовано)
        if from_lower == to_unit.lower():
            continue
        # Проверить совпадение названия показателя
        for keyword in test_keywords:
            if keyword in test_lower or test_lower in keyword:
                return to_unit, factor
    return None, None


def get_reference(test_name: str) -> tuple:
    """Получить референсные значения для показателя. Возвращает (min, max, unit) или (None, None, None)."""
    test_lower = test_name.lower().strip()

    # Показатели мочи — не применять референсы из крови
    if test_lower in URINE_ONLY_TESTS:
        return None, None, None

    # Точное совпадение
    if test_lower in REFERENCE_VALUES:
        ref = REFERENCE_VALUES[test_lower]
        return ref[0], ref[1], ref[2]

    # Частичное совпадение — более строгое: ключ должен быть подстрокой названия
    for key, ref in REFERENCE_VALUES.items():
        if key in test_lower:
            return ref[0], ref[1], ref[2]

    return None, None, None


def calculate_status(value_str: str, ref_min: str, ref_max: str) -> str:
    """Рассчитать статус на основе значения и референса."""
    try:
        value = float(str(value_str).replace(",", "."))
        rmin = float(str(ref_min).replace(",", ".")) if ref_min else None
        rmax = float(str(ref_max).replace(",", ".")) if ref_max else None
    except (ValueError, TypeError):
        return "unknown"

    if rmin is not None and value < rmin:
        return "low"
    if rmax is not None and value > rmax:
        return "high"
    if rmin is not None and rmax is not None:
        return "normal"
    return "unknown"


def normalize_csv(csv_path: Path, dry_run: bool = False) -> list:
    """Нормализовать один CSV-файл. Возвращает список изменений."""
    changes = []

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Убедиться, что есть нужные колонки
    required = {"date", "test_name", "value", "unit", "reference_min", "reference_max", "status", "source_file"}
    if not required.issubset(set(fieldnames)):
        missing = required - set(fieldnames)
        print(f"  Предупреждение: в {csv_path.name} отсутствуют колонки: {missing}", file=sys.stderr)

    normalized_rows = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        test_name = row.get("test_name", "")
        value = row.get("value", "")
        unit = row.get("unit", "")
        ref_min = row.get("reference_min", "")
        ref_max = row.get("reference_max", "")
        status = row.get("status", "")

        # 1. Конверсия единиц
        to_unit, factor = find_unit_conversion(test_name, unit)
        if to_unit and factor:
            try:
                old_value = float(str(value).replace(",", "."))
                new_value = round(old_value * factor, 4)
                changes.append({
                    "file": csv_path.name, "row": i, "field": "value+unit",
                    "original_value": f"{value} {unit}",
                    "normalized_value": f"{new_value} {to_unit}",
                    "change_type": "unit_conversion"
                })
                new_row["value"] = str(new_value)
                new_row["unit"] = to_unit
                unit = to_unit
                value = str(new_value)
                # Конвертировать референсные значения тоже
                if ref_min:
                    try:
                        new_row["reference_min"] = str(round(float(str(ref_min).replace(",", ".")) * factor, 4))
                        ref_min = new_row["reference_min"]
                    except ValueError:
                        pass
                if ref_max:
                    try:
                        new_row["reference_max"] = str(round(float(str(ref_max).replace(",", ".")) * factor, 4))
                        ref_max = new_row["reference_max"]
                    except ValueError:
                        pass
            except (ValueError, TypeError):
                pass

        # 2. Заполнение референсных значений
        if not ref_min or not ref_max:
            std_min, std_max, std_unit = get_reference(test_name)
            if std_min is not None:
                if not ref_min:
                    new_row["reference_min"] = str(std_min)
                    ref_min = str(std_min)
                    changes.append({
                        "file": csv_path.name, "row": i, "field": "reference_min",
                        "original_value": "", "normalized_value": str(std_min),
                        "change_type": "reference_filled"
                    })
                if not ref_max:
                    new_row["reference_max"] = str(std_max)
                    ref_max = str(std_max)
                    changes.append({
                        "file": csv_path.name, "row": i, "field": "reference_max",
                        "original_value": "", "normalized_value": str(std_max),
                        "change_type": "reference_filled"
                    })

        # 3. Пересчёт статуса
        if ref_min and ref_max and value:
            new_status = calculate_status(value, ref_min, ref_max)
            if new_status != status and new_status != "unknown":
                changes.append({
                    "file": csv_path.name, "row": i, "field": "status",
                    "original_value": status, "normalized_value": new_status,
                    "change_type": "status_corrected"
                })
                new_row["status"] = new_status

        normalized_rows.append(new_row)

    # Записать обратно
    if not dry_run and changes:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(normalized_rows)
        print(f"  Сохранено: {csv_path.name} ({len(changes)} изменений)")
    elif dry_run:
        print(f"  [dry-run] {csv_path.name}: {len(changes)} изменений (не сохранено)")
    else:
        print(f"  Без изменений: {csv_path.name}")

    return changes


def save_log(all_changes: list, log_path: Path):
    """Сохранить лог нормализации."""
    fieldnames = ["file", "row", "field", "original_value", "normalized_value", "change_type"]
    with open(log_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_changes)
    print(f"\nЛог сохранён: {log_path} ({len(all_changes)} записей)")


def main():
    parser = argparse.ArgumentParser(
        description="Нормализация единиц измерения и заполнение референсных значений в CSV-таблицах.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python3 scripts/normalize_values.py --all
  python3 scripts/normalize_values.py --file 02_TABLES/blood_biochemistry.csv
  python3 scripts/normalize_values.py --all --dry-run
        """
    )
    parser.add_argument("--file", help="Путь к конкретному CSV-файлу")
    parser.add_argument("--all", action="store_true", help="Обработать все CSV в 02_TABLES/")
    parser.add_argument("--dry-run", action="store_true", help="Показать изменения без сохранения")
    args = parser.parse_args()

    if not args.file and not args.all:
        parser.print_help()
        sys.exit(1)

    tables_dir = Path("02_TABLES")
    if not tables_dir.exists():
        print(f"Ошибка: папка {tables_dir} не найдена. Запускайте из корня проекта.", file=sys.stderr)
        sys.exit(1)

    files_to_process = []
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"Ошибка: файл не найден: {p}", file=sys.stderr)
            sys.exit(1)
        files_to_process = [p]
    else:
        files_to_process = list(tables_dir.glob("*.csv"))
        # Исключить лог-файлы
        files_to_process = [f for f in files_to_process if "log" not in f.name.lower()]

    if not files_to_process:
        print("Нет CSV-файлов для обработки.")
        sys.exit(0)

    print(f"Обработка {len(files_to_process)} файлов{'  [dry-run]' if args.dry_run else ''}...")
    all_changes = []
    for csv_file in sorted(files_to_process):
        print(f"\n{csv_file.name}:")
        changes = normalize_csv(csv_file, dry_run=args.dry_run)
        all_changes.extend(changes)

    if all_changes and not args.dry_run:
        log_path = tables_dir / "normalization_log.csv"
        save_log(all_changes, log_path)

    print(f"\nГотово. Всего изменений: {len(all_changes)}")


if __name__ == "__main__":
    main()
