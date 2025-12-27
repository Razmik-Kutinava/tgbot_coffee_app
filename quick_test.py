#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
print("Начало теста...")
print(f"Python: {sys.version}")

try:
    print("Импорт supabase...")
    from supabase import create_client
    print("✅ Supabase импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

SUPABASE_URL = "https://wntvxdgxzenehfzvorae.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTExNDEwOCwiZXhwIjoyMDgwNjkwMTA4fQ.xea_k8DBEUjPO1ThPGgwxkAwsH2SnRIgxfiPpRhy9kk"

try:
    print("Создание клиента...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Клиент создан")
    
    print("\nПроверка таблицы Order...")
    response = supabase.table("Order").select("id").limit(1).execute()
    print(f"✅ Таблица Order доступна. Записей: {len(response.data) if response.data else 0}")
    
    if response.data:
        print("\nПолучение полной структуры одного заказа...")
        full_response = supabase.table("Order").select("*").limit(1).execute()
        if full_response.data:
            order = full_response.data[0]
            print("Поля в таблице Order:")
            for key in sorted(order.keys()):
                print(f"  - {key}")
    
    print("\nПроверка таблицы User...")
    user_response = supabase.table("User").select("id").limit(1).execute()
    print(f"✅ Таблица User доступна. Записей: {len(user_response.data) if user_response.data else 0}")
    
    if user_response.data:
        print("\nПолучение полной структуры одного пользователя...")
        full_user = supabase.table("User").select("*").limit(1).execute()
        if full_user.data:
            user = full_user.data[0]
            print("Поля в таблице User:")
            for key in sorted(user.keys()):
                print(f"  - {key}")
    
    print("\n✅ Все проверки пройдены!")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

