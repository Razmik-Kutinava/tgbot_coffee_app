#!/usr/bin/env python
# -*- coding: utf-8 -*-
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wntvxdgxzenehfzvorae.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0")

print("=" * 60)
print("ТЕСТ ПОДКЛЮЧЕНИЯ К SUPABASE С ANON KEY")
print("=" * 60)
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_ANON_KEY[:50]}...")
print()

try:
    print("Создание клиента...")
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Клиент создан успешно!")
    
    print("\nПроверка таблицы Order...")
    try:
        response = supabase.table("Order").select("id").limit(3).execute()
        print(f"✅ Таблица Order доступна!")
        print(f"   Найдено записей: {len(response.data) if response.data else 0}")
        
        if response.data:
            print("\nПоследние 3 заказа:")
            for i, order in enumerate(response.data, 1):
                print(f"   {i}. ID: {order.get('id')}")
    except Exception as e:
        print(f"❌ Ошибка при доступе к Order: {e}")
    
    print("\nПроверка таблицы User...")
    try:
        response = supabase.table("User").select("id").limit(1).execute()
        print(f"✅ Таблица User доступна!")
        print(f"   Найдено записей: {len(response.data) if response.data else 0}")
    except Exception as e:
        print(f"❌ Ошибка при доступе к User: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ПОДКЛЮЧЕНИЕ РАБОТАЕТ!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
    import traceback
    traceback.print_exc()

