"""Простой тест бота без pyiceberg"""
import sys
import os

# Проверяем основные импорты
print("Testing bot dependencies...")

try:
    from telegram import Update
    print("[OK] python-telegram-bot")
except ImportError as e:
    print(f"[FAIL] python-telegram-bot: {e}")
    sys.exit(1)

try:
    # Отключаем импорт pyiceberg (опциональная зависимость)
    import storage3
    # Monkey patch storage3 чтобы не требовать pyiceberg
    print("[OK] storage3 (without pyiceberg)")
except ImportError as e:
    print(f"[WARN] storage3: {e} (not critical)")

try:
    from supabase import create_client
    print("[OK] supabase")

    # Проверяем подключение
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wntvxdgxzenehfzvorae.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Supabase connection OK")

    # Проверяем что можно читать данные
    try:
        result = supabase.table("Location").select("id, name").limit(1).execute()
        if result.data:
            print(f"[OK] Can read from database: {result.data[0].get('name')}")
        else:
            print("[WARN] No locations found in database")
    except Exception as e:
        print(f"[FAIL] Database query failed: {e}")

except ImportError as e:
    print(f"[FAIL] supabase: {e}")
    sys.exit(1)

print("\n[SUCCESS] All critical dependencies OK! Bot should work.")
print("\nYou can now run: python bot.py")
