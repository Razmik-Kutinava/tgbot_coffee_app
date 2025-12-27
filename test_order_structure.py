from supabase import create_client
import json

SUPABASE_URL = "https://wntvxdgxzenehfzvorae.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTExNDEwOCwiZXhwIjoyMDgwNjkwMTA4fQ.xea_k8DBEUjPO1ThPGgwxkAwsH2SnRIgxfiPpRhy9kk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ Order")
print("=" * 60)

try:
    # Получаем один заказ чтобы увидеть структуру
    response = supabase.table("Order").select("*").limit(1).execute()
    
    if response.data and len(response.data) > 0:
        order = response.data[0]
        print("\n✅ Структура одного заказа:")
        print(json.dumps(order, indent=2, default=str))
        
        print("\n" + "=" * 60)
        print("ПОЛУЧЕНИЕ ПОСЛЕДНИХ 3 ЗАКАЗОВ")
        print("=" * 60)
        
        # Получаем последние 3 заказа
        response = supabase.table("Order").select("*").order("createdAt", desc=True).limit(3).execute()
        
        if response.data:
            print(f"\n✅ Найдено {len(response.data)} заказов:\n")
            for i, order in enumerate(response.data, 1):
                print(f"Заказ {i}:")
                print(f"  ID: {order.get('id')}")
                print(f"  userId: {order.get('userId')}")
                print(f"  status: {order.get('status')}")
                print(f"  createdAt: {order.get('createdAt')}")
                print(f"  total: {order.get('total')}")
                print()
        else:
            print("❌ Заказы не найдены")
    else:
        print("❌ Таблица Order пуста или недоступна")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

