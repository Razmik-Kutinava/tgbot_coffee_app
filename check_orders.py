from supabase import create_client

SUPABASE_URL = "https://wntvxdgxzenehfzvorae.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTExNDEwOCwiZXhwIjoyMDgwNjkwMTA4fQ.xea_k8DBEUjPO1ThPGgwxkAwsH2SnRIgxfiPpRhy9kk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Проверка таблицы Order...\n")

# Получаем один заказ чтобы посмотреть структуру
try:
    response = supabase.table("Order").select("*").limit(1).execute()
    if response.data and len(response.data) > 0:
        order = response.data[0]
        print("Структура таблицы Order:")
        print("-" * 50)
        for key, value in order.items():
            print(f"{key}: {type(value).__name__} = {value}")
        print("-" * 50)
        
        # Пробуем получить последние 3 оплаченных заказа
        print("\n\nПопытка получить последние 3 оплаченных заказа...")
        
        # Пробуем разные варианты статусов
        status_variants = ["paid", "completed", "PAID", "COMPLETED", "оплачен", "Оплачен"]
        
        for status in status_variants:
            try:
                response = supabase.table("Order").select("*").eq("status", status).order("createdAt", desc=True).limit(3).execute()
                if response.data and len(response.data) > 0:
                    print(f"\n✅ Найдено {len(response.data)} заказов со статусом '{status}':")
                    for i, order in enumerate(response.data, 1):
                        print(f"\nЗаказ {i}:")
                        print(f"  ID: {order.get('id')}")
                        print(f"  Статус: {order.get('status')}")
                        print(f"  Дата: {order.get('createdAt')}")
                    break
            except Exception as e:
                continue
        
        # Если не нашли по статусу, просто берем последние 3
        print("\n\nПолучаем последние 3 заказа (без фильтра по статусу)...")
        response = supabase.table("Order").select("*").order("createdAt", desc=True).limit(3).execute()
        if response.data:
            print(f"✅ Найдено {len(response.data)} последних заказов:")
            for i, order in enumerate(response.data, 1):
                print(f"\nЗаказ {i}:")
                print(f"  ID: {order.get('id')}")
                print(f"  Статус: {order.get('status')}")
                print(f"  Дата создания: {order.get('createdAt')}")
                print(f"  Все поля: {list(order.keys())}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

