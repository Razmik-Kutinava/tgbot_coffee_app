import logging
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки Supabase
SUPABASE_URL = "https://wntvxdgxzenehfzvorae.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTExNDEwOCwiZXhwIjoyMDgwNjkwMTA4fQ.xea_k8DBEUjPO1ThPGgwxkAwsH2SnRIgxfiPpRhy9kk"

print("Проверка подключения к Supabase...")
print(f"URL: {SUPABASE_URL}")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Подключение к Supabase установлено!")
    
    # Проверяем таблицы
    print("\nПроверка таблицы 'users'...")
    try:
        response = supabase.table("users").select("telegram_id").limit(1).execute()
        print(f"✅ Таблица 'users' доступна. Найдено записей: {len(response.data) if response.data else 0}")
    except Exception as e:
        print(f"❌ Ошибка при доступе к таблице 'users': {e}")
    
    print("\nПроверка таблицы 'orders'...")
    try:
        response = supabase.table("orders").select("id").limit(1).execute()
        print(f"✅ Таблица 'orders' доступна. Найдено записей: {len(response.data) if response.data else 0}")
    except Exception as e:
        print(f"❌ Ошибка при доступе к таблице 'orders': {e}")
    
    print("\n✅ Подключение работает!")
    
except Exception as e:
    print(f"❌ Ошибка при подключении к Supabase: {e}")
    import traceback
    traceback.print_exc()

