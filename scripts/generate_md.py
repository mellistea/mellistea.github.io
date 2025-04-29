import os
import re
from datetime import datetime

# Папки
TXT_FOLDER = "txt"
POSTS_FOLDER = "_posts"

# Убедимся, что папка для постов существует
os.makedirs(POSTS_FOLDER, exist_ok=True)

def slugify(text):
    """Убираем все русские буквы и спецсимволы для имени файла."""
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # удаляем всё не-ASCII
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-').lower()

def indent_multiline(text, spaces=2):
    """Отступает каждую строку на заданное количество пробелов."""
    padding = ' ' * spaces
    return '\n'.join(padding + line if line.strip() else '' for line in text.splitlines())

def extract_fields(text):
    """Извлекаем все поля из текстового файла."""
    fields = {
        "title": "",
        "ficbook_link": "",
        "author": "",
        "author_link": "",
        "fandom": "",
        "pairing": "",
        "rating": "",
        "size": "",
        "parts": "",
        "status": "",
        "tags": "",
        "description": "",
        "notes": "",
        "other_publications": "",
        "content": ""
    }

    lines = text.splitlines()
    print(f"[DEBUG] Количество строк в файле: {len(lines)}")

    inside_description = False
    inside_notes = False
    passed_info_block = False
    description_collector = []
    notes_collector = []
    content_collector = []

    for idx, line in enumerate(lines):
        line = line.strip()

        if not fields["title"] and line and not line.startswith("*") and not line.startswith("="):
            fields["title"] = line
            continue

        if not fields["ficbook_link"] and "ficbook.net/readfic/" in line:
            fields["ficbook_link"] = line
            continue

        if line.startswith("Автор:"):
            match = re.match(r"Автор:\s*(.+)\((https?://.+)\)", line)
            if match:
                fields["author"] = match.group(1).strip()
                fields["author_link"] = match.group(2).strip()

        elif line.startswith("Фэндом:"):
            fields["fandom"] = line.split(":", 1)[1].strip()

        elif line.startswith("Пэйринг") or line.startswith("Пэйринг и персонажи:"):
            fields["pairing"] = line.split(":", 1)[1].strip()

        elif line.startswith("Рейтинг:"):
            fields["rating"] = line.split(":", 1)[1].strip()

        elif line.startswith("Размер:"):
            fields["size"] = line.split(":", 1)[1].strip()

        elif line.startswith("Кол-во частей:"):
            fields["parts"] = line.split(":", 1)[1].strip()

        elif line.startswith("Статус:"):
            fields["status"] = line.split(":", 1)[1].strip()

        elif line.startswith("Метки:"):
            fields["tags"] = line.split(":", 1)[1].strip()

        elif line.startswith("Описание:"):
            inside_description = True
            continue

        elif line.startswith("Примечания:"):
            inside_description = False
            inside_notes = True
            continue

        elif line.startswith("Публикация на других ресурсах:"):
            fields["other_publications"] = line.split(":", 1)[1].strip()
            continue

        elif re.match(r"^=+.*=+$", line):
            inside_description = False
            inside_notes = False
            passed_info_block = True
            content_collector.append(line)
            continue

        if inside_description:
            description_collector.append(line)

        elif inside_notes:
            notes_collector.append(line)

        elif passed_info_block:
            content_collector.append(line)

    fields["description"] = " ".join(description_collector).strip()
    fields["notes"] = "\n".join(notes_collector).strip()
    fields["content"] = "\n".join(content_collector).strip()

    print(f"[DEBUG] Извлечено название: {fields['title']}")
    print(f"[DEBUG] Извлечён автор: {fields['author']}")
    print(f"[DEBUG] Извлечён рейтинг: {fields['rating']}")
    print(f"[DEBUG] Длина основного текста: {len(fields['content'])} символов")

    return fields

def generate_post(fields, original_filename):
    today = datetime.today().strftime('%Y-%m-%d')
    base_name = os.path.splitext(original_filename)[0]
    slug = slugify(base_name)
    filename = f"{today}-{slug}.md"

    output_path = os.path.join(POSTS_FOLDER, filename)

    if os.path.exists(output_path):
        print(f"[SKIP] Файл уже существует, пропуск: {output_path}")
        return

    front_matter = f"""---
layout: story
title: "{fields['title']}"
author: "{fields['author']}"
author_link: "{fields['author_link']}"
ficbook_link: "{fields['ficbook_link']}"
rating: "{fields['rating']}"
fandom: "{fields['fandom']}"
pairing: "{fields['pairing']}"
size: "{fields['size']}"
parts: "{fields['parts']}"
status: "{fields['status']}"
tags: "{fields['tags']}"
description: "{fields['description']}"
other_publications: "{fields['other_publications']}"
notes: |
{indent_multiline(fields['notes'], 2)}
---
"""

    full_text = front_matter + "\n" + fields["content"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"[+] Сгенерирован файл: {output_path}")

def main():
    if not os.path.exists(TXT_FOLDER):
        print(f"[ERROR] Папка {TXT_FOLDER} не найдена.")
        return

    files = [f for f in os.listdir(TXT_FOLDER) if f.endswith(".txt")]

    if not files:
        print("[!] Нет файлов .txt в папке /txt/")
        return

    for file in files:
        print(f"[INFO] Обработка файла: {file}")
        path = os.path.join(TXT_FOLDER, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        fields = extract_fields(text)
        if fields and fields["content"]:
            generate_post(fields, file)
        else:
            print(f"[WARNING] Пропуск файла: {file} — не удалось извлечь текст.")

if __name__ == "__main__":
    main()