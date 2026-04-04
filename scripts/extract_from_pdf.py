#!/usr/bin/env python3
"""
extract_from_pdf.py — Извлечение текста и таблиц из PDF-файлов.

Использование:
    python3 scripts/extract_from_pdf.py <путь_к_pdf> [--output text|json] [--tables] [--page N]

Примеры:
    python3 scripts/extract_from_pdf.py 01_SORTED/blood/2024-03-15_blood_ОАК.pdf
    python3 scripts/extract_from_pdf.py 01_SORTED/blood/2024-03-15_blood_ОАК.pdf --output json
    python3 scripts/extract_from_pdf.py 01_SORTED/blood/2024-03-15_blood_ОАК.pdf --tables
"""

import argparse
import json
import sys
from pathlib import Path


def extract_text_fitz(pdf_path: Path) -> dict:
    """Извлечение текста с помощью PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("Ошибка: PyMuPDF не установлен. Запустите: pip3 install PyMuPDF", file=sys.stderr)
        sys.exit(1)

    result = {
        "file": str(pdf_path),
        "pages": [],
        "full_text": "",
        "metadata": {}
    }

    with fitz.open(str(pdf_path)) as doc:
        result["metadata"] = {
            "page_count": doc.page_count,
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
        }

        all_text_parts = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            result["pages"].append({
                "page": page_num,
                "text": text
            })
            all_text_parts.append(text)

        result["full_text"] = "\n".join(all_text_parts)

    return result


def extract_tables_camelot(pdf_path: Path, pages: str = "all") -> list:
    """Извлечение таблиц с помощью camelot."""
    try:
        import camelot
    except ImportError:
        print("camelot-py не установлен, пробуем tabula...", file=sys.stderr)
        return extract_tables_tabula(pdf_path, pages)

    tables_data = []
    try:
        tables = camelot.read_pdf(str(pdf_path), pages=pages, flavor="lattice")
        if len(tables) == 0:
            tables = camelot.read_pdf(str(pdf_path), pages=pages, flavor="stream")

        for i, table in enumerate(tables):
            df = table.df
            tables_data.append({
                "table_index": i,
                "page": table.page,
                "accuracy": table.accuracy,
                "rows": df.values.tolist(),
                "headers": df.iloc[0].tolist() if not df.empty else []
            })
    except Exception as e:
        print(f"Ошибка camelot: {e}", file=sys.stderr)
        return extract_tables_tabula(pdf_path, pages)

    return tables_data


def extract_tables_tabula(pdf_path: Path, pages: str = "all") -> list:
    """Резервное извлечение таблиц с помощью tabula."""
    try:
        import tabula
    except ImportError:
        print("tabula-py не установлен. Запустите: pip3 install tabula-py", file=sys.stderr)
        return []

    tables_data = []
    try:
        dfs = tabula.read_pdf(str(pdf_path), pages=pages, multiple_tables=True)
        for i, df in enumerate(dfs):
            tables_data.append({
                "table_index": i,
                "page": "unknown",
                "accuracy": None,
                "rows": df.values.tolist(),
                "headers": df.columns.tolist()
            })
    except Exception as e:
        print(f"Ошибка tabula: {e}", file=sys.stderr)

    return tables_data


def main():
    parser = argparse.ArgumentParser(
        description="Извлечение текста и таблиц из PDF медицинских документов.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python3 scripts/extract_from_pdf.py doc.pdf
  python3 scripts/extract_from_pdf.py doc.pdf --output json > result.json
  python3 scripts/extract_from_pdf.py doc.pdf --tables --output json
  python3 scripts/extract_from_pdf.py doc.pdf --page 1
        """
    )
    parser.add_argument("pdf_path", help="Путь к PDF-файлу")
    parser.add_argument(
        "--output", choices=["text", "json"], default="text",
        help="Формат вывода: text (по умолчанию) или json"
    )
    parser.add_argument(
        "--tables", action="store_true",
        help="Также извлечь таблицы (требует camelot или tabula)"
    )
    parser.add_argument(
        "--page", type=int, default=None,
        help="Извлечь только конкретную страницу (нумерация с 1)"
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Ошибка: файл не найден: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Предупреждение: файл не имеет расширения .pdf: {pdf_path}", file=sys.stderr)

    # Извлечение текста
    data = extract_text_fitz(pdf_path)

    # Фильтрация по странице
    if args.page is not None:
        pages = [p for p in data["pages"] if p["page"] == args.page]
        data["pages"] = pages
        data["full_text"] = "\n".join(p["text"] for p in pages)

    # Извлечение таблиц
    if args.tables:
        pages_str = str(args.page) if args.page else "all"
        data["tables"] = extract_tables_camelot(pdf_path, pages=pages_str)

    # Вывод
    if args.output == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"=== Файл: {pdf_path} ===")
        print(f"Страниц: {data['metadata'].get('page_count', '?')}")
        print()
        if args.page:
            pages_to_print = data["pages"]
        else:
            pages_to_print = data["pages"]
        for page in pages_to_print:
            print(f"--- Страница {page['page']} ---")
            print(page["text"])
        if args.tables and "tables" in data:
            print(f"\n=== Таблицы ({len(data['tables'])} шт.) ===")
            for table in data["tables"]:
                print(f"\nТаблица {table['table_index'] + 1} (стр. {table['page']}):")
                for row in table["rows"]:
                    print("  |", " | ".join(str(cell) for cell in row), "|")


if __name__ == "__main__":
    main()
