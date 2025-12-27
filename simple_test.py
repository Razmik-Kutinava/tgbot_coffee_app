#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("Загрузка переменных окружения...")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:50] if SUPABASE_KEY else 'НЕ НАЙДЕН'}...")

try:
    print("\nИмпорт supabase...")
    from supabase import create_client
    print("✅ Импорт успешен")
    
    print("\nСоздание клиента...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Клиент создан")
    
    print("\nПроверка таблицы Order...")
    response = supabase.table("Order").select("id").limit(3).execute()
    print(f"✅ Таблица Order доступна!")
    print(f"   Найдено записей: {len(response.data) if response.data else 0}")
    
    if response.data:
        print("\nПоследние 3 заказа:")
        for i, order in enumerate(response.data, 1):
            print(f"   {i}. ID: {order.get('id')}")
    
    print("\n✅ ВСЕ РАБОТАЕТ!")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Попробуйте: pip install supabase")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

