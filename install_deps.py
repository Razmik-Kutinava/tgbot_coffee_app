#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys

print("Установка совместимых версий зависимостей...")

packages = [
    "python-telegram-bot==21.6",
    "supabase==2.3.0",
    "realtime==2.3.0", 
    "postgrest==0.16.0",
    "gotrue==2.6.0",
    "python-dotenv==1.0.0"
]

for package in packages:
    print(f"\nУстановка {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--upgrade", "--force-reinstall"])
        print(f"✅ {package} установлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при установке {package}: {e}")

print("\n✅ Установка завершена!")
print("\nПроверка импорта...")
try:
    from supabase import create_client
    print("✅ Supabase импортирован успешно")
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")

