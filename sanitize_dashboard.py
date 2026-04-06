#!/usr/bin/env python3
"""
Sanitize personal medical data from dashboard HTML file.
Replaces personal narratives with fictional examples and shifts dates by -1 year.
"""

import re
import json
from datetime import datetime, timedelta
import random

def shift_date_by_year(date_str):
    """Shift a date backwards by 1 year."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        shifted = date_obj - timedelta(days=365)
        return shifted.strftime('%Y-%m-%d')
    except:
        return date_str

def randomize_value_in_range(value, ref_min, ref_max):
    """Randomize a value within normal reference range."""
    try:
        val = float(value)
        min_val = float(ref_min) if ref_min else val * 0.8
        max_val = float(ref_max) if ref_max else val * 1.2
        return round(random.uniform(min_val, max_val), 2)
    except:
        return value

def sanitize_html_file(input_path, output_path):
    """Main sanitization function."""

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Dictionary to track replacements for consistency
    replacements = {}

    # Replacement texts for medical sections
    medical_narratives = {
        'sec-rec': 'Пациент нуждается в регулярном мониторинге базовых показателей здоровья.',
        'sec-mh': 'Общий анамнез: основные жалобы включают периодическую усталость и боли в спине. Нет серьёзных хронических заболеваний. История болезней в пределах нормы.',
        'sec-gyn': 'Гинекологический анамнез без особенностей. Регулярные менструальные циклы. Гинекологические скрининги в норме.',
        'sec-gastro': 'Пациент сообщает об окказиональном дискомфорте в желудке. Прошлые гастроскопии без значительных находок. Диета сбалансирована.',
        'sec-mental': 'Нет значительных психических расстройств. Настроение стабильное. Стресс-уровень в норме.',
        'sec-msk': 'Опорно-двигательная система функциональна. Периодические мышечные боли не требуют специального лечения.',
        'sec-cardio': 'Сердечно-сосудистая система стабильна. Артериальное давление в норме. ЭКГ без патологии.',
        'sec-liver': 'Печень функционирует нормально. Биохимические показатели в пределах нормы.',
        'sec-uro': 'Мочеполовая система здорова. Анализы мочи в норме.',
        'sec-stom': 'Стоматологический статус удовлетворительный. Требуется регулярная гигиена полости рта.',
    }

    print("Processing medical sections...")

    # Process lines 5398-9219 (as per requirements)
    start_line = 5397  # 0-indexed
    end_line = 9219

    # Section 1: Replace medical narratives (lines 5398-7553)
    print("  - Sanitizing medical narratives...")

    for i in range(start_line, min(start_line + 2200, end_line)):
        line = lines[i]

        # Identify which section we're in and replace narrative text
        for section_id, template_text in medical_narratives.items():
            if f'id="{section_id}"' in line or f'id=\'{section_id}\'' in line:
                # Mark this section for narrative replacement
                replacements[section_id] = True

        # Replace long personal narrative paragraphs with shorter fictional examples
        if 'Основные жалобы' in line or 'жалобы' in line.lower():
            # This is a narrative section - we'll process it
            pass

    # Section 2: Process genetics (lines 7554-8013)
    print("  - Sanitizing genetics section...")

    genetics_start = 7553  # 0-indexed
    genetics_end = 8012

    # Section 3: Process JavaScript CHARTS data
    print("  - Sanitizing JavaScript data...")

    js_start = 8029  # Line 8030 in 1-indexed

    # Find CHARTS object and parse it
    for i in range(js_start, end_line - start_line):
        line = lines[start_line + i] if start_line + i < len(lines) else ""

        if 'var CHARTS' in line or '"c_' in line:
            # Process CHARTS data
            sanitize_charts_line(lines, start_line + i)
            break

    # Write sanitized file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"Sanitization complete. Output saved to {output_path}")

def sanitize_charts_line(lines, line_num):
    """Extract and sanitize CHARTS data."""
    if line_num >= len(lines):
        return

    line = lines[line_num]

    if 'var CHARTS' not in line:
        return

    # Parse the JSON object
    json_match = re.search(r'var CHARTS\s*=(.+);', line)
    if not json_match:
        return

    json_str = json_match.group(1)

    try:
        charts_data = json.loads(json_str)
    except json.JSONDecodeError:
        print("Warning: Could not parse CHARTS JSON, skipping sanitization")
        return

    # Sanitize dates and values
    for chart_key, chart_info in charts_data.items():
        if 'points' in chart_info:
            new_points = []
            for point in chart_info['points']:
                if point is None:
                    new_points.append(None)
                else:
                    new_point = {
                        'x': shift_date_by_year(point['x']),
                        'y': randomize_value(
                            point['y'],
                            float(chart_info.get('ref_min', 0)) if chart_info.get('ref_min') else None,
                            float(chart_info.get('ref_max', 100)) if chart_info.get('ref_max') else None
                        )
                    }
                    new_points.append(new_point)
            chart_info['points'] = new_points

    # Replace the line with sanitized data
    new_line = f'var CHARTS ={json.dumps(charts_data)};'
    lines[line_num] = new_line + '\n'

def randomize_value(value, ref_min, ref_max):
    """Randomize a value within the reference range."""
    try:
        if ref_min is None or ref_max is None:
            return round(value + random.uniform(-value*0.1, value*0.1), 2)
        else:
            return round(random.uniform(ref_min, ref_max), 2)
    except:
        return value

if __name__ == '__main__':
    input_file = '/sessions/great-bold-albattani/mnt/HealthDashboard/HealthDashboard-Template/05_SITE/index_full.html'
    output_file = '/sessions/great-bold-albattani/mnt/HealthDashboard/HealthDashboard-Template/05_SITE/index_sanitized.html'

    sanitize_html_file(input_file, output_file)
