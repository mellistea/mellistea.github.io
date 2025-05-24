# scripts/deploy.py

import os
import subprocess
from pathlib import Path

# ========== НАСТРОЙКИ ==========

GIT_NAME = "имя"         # ← Имя для подписи в коммитах
GIT_EMAIL = "имейл"  # ← Твой GitHub-почтовый адрес
REPO_URL = "https://токен@github.com/mellistea/mellistea.github.io.git"
COMMIT_MSG = "Auto-deploy Jekyll site"

# Папка проекта — на уровень выше scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run(cmd, allow_fail=False):
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True, capture_output=True, text=True)
    if result.stdout: print(result.stdout)
    if result.stderr: print(result.stderr)
    if result.returncode != 0 and not allow_fail:
        raise Exception(f"Ошибка команды: {cmd}")
    return result

def main():
    # Установим имя и email явно
    run(f'git config user.name "{GIT_NAME}"')
    run(f'git config user.email "{GIT_EMAIL}"')

    # Репозиторий
    if not (PROJECT_ROOT / ".git").exists():
        run("git init")
        run(f"git remote add origin {REPO_URL}")
    else:
        run(f"git remote set-url origin {REPO_URL}")

    run("git add .")

    status = run("git status --porcelain", allow_fail=True)
    if status.stdout.strip():  # есть изменения
        run(f'git commit -m "{COMMIT_MSG}"')
    else:
        print("Нет изменений — коммит пропущен.")

    run("git branch -M main")
    run("git push -u origin main --force")


if __name__ == "__main__":
    main()
