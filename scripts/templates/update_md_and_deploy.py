# scripts/update_md_and_deploy.py

import os
import re
import subprocess
import frontmatter
from datetime import datetime
from pathlib import Path
from unidecode import unidecode

# ========== НАСТРОЙКИ ==========
GIT_NAME = "имя"
GIT_EMAIL = "имейл"
REPO_URL = "https://токен@github.com/mellistea/mellistea.github.io.git"
COMMIT_MSG = "автообновление фанфиков"
SOURCE_ROOT = Path(r"D:\Dropbox\obsidian\memo\Fic\Законченные")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"

# ========== УТИЛИТЫ ==========
def run(cmd, allow_fail=False):
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True, capture_output=True, text=True)
    print(f"\n>>> {cmd}")
    if result.stdout: print(result.stdout)
    if result.stderr: print(result.stderr)
    if result.returncode != 0 and not allow_fail:
        raise Exception(f"Ошибка команды: {cmd}")
    return result

def transliterate(text):
    return re.sub(r"[^\w\-]", "-", unidecode(text)).strip("-")

def get_file_info(path: Path):
    stat = path.stat()
    return int(stat.st_mtime), stat.st_size

# ========== ОСНОВНАЯ ЛОГИКА ==========
def update_posts():
    print(f"\n🔍 Ищем файлы с 🪶 в: {SOURCE_ROOT}\n")

    for dirpath, _, filenames in os.walk(SOURCE_ROOT):
        for fname in filenames:
            if "🪶" not in fname or not fname.endswith(".md"):
                continue

            source_path = Path(dirpath) / fname
            print(f"📄 Найден файл: {source_path}")

            try:
                post = frontmatter.load(source_path)
            except Exception as e:
                print(f"⚠️ Ошибка чтения frontmatter: {e}")
                continue

            date_str = post.get("date")
            title = post.get("title")

            if not date_str or not title:
                print(f"⚠️ Пропущен {fname}: нет поля date или title")
                continue

            try:
                date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
            except Exception as e:
                print(f"⚠️ Неверный формат даты в {fname}: {e}")
                continue

            translit_title = transliterate(title)
            new_filename = f"{date}-{translit_title}.md"
            dest_path = POSTS_DIR / new_filename

            src_mtime, src_size = get_file_info(source_path)
            if dest_path.exists():
                dst_mtime, dst_size = get_file_info(dest_path)
                if src_mtime == dst_mtime and src_size == dst_size:
                    print(f"✅ Без изменений: {new_filename}")
                    continue
                else:
                    print(f"📝 Обновляется: {new_filename}")
            else:
                print(f"🆕 Новый файл: {new_filename}")

            post["layout"] = "story"
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
            os.utime(dest_path, (src_mtime, src_mtime))

def deploy():
    run(f'git config user.name "{GIT_NAME}"')
    run(f'git config user.email "{GIT_EMAIL}"')

    if not (PROJECT_ROOT / ".git").exists():
        run("git init")
        run(f"git remote add origin {REPO_URL}")
    else:
        run(f"git remote set-url origin {REPO_URL}")

    run("git add .")
    status = run("git status --porcelain", allow_fail=True)

    if status.stdout.strip():
        run(f'git commit -m "{COMMIT_MSG}"')
    else:
        print("🚫 Нет изменений — коммит пропущен.")

    run("git branch -M main")
    run("git push -u origin main --force")

if __name__ == "__main__":
    update_posts()
    deploy()
    input("\n✔️ Готово. Нажми Enter, чтобы закрыть окно...")
