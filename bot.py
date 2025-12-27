import logging
import sys
import os
from typing import Dict, List, Optional

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, MenuButtonWebApp, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Пробуем загрузить dotenv, но не критично если не получится
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Настройка логирования для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Пробуем импортировать supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Supabase не установлен: {e}")
    SUPABASE_AVAILABLE = False
    Client = None

# Токен бота
BOT_TOKEN = "7969044420:AAESP3djIFLWDOis9H4gsd7S_t1-iDA1MQU"

# Ссылка на мини-приложение
WEB_APP_URL = "https://fl-mini-app-v3.onrender.com"

# URL картинки/баннера (можно оставить None, если картинка не нужна)
BANNER_IMAGE_URL = None  # Например: "https://example.com/banner.jpg"

# Ссылка на промо-акции
PROMO_LINK_URL = "https://cdn.dodostatic.net/static/partner/ru/promo.html"

# Базовый URL для документов
DOCUMENTS_BASE_URL = "https://domin.site.net"

# URL для программы благодарности (PDF из Google Drive)
GRATITUDE_PROGRAM_URL = "https://drive.google.com/file/d/1ABC123XYZ/view"  # Замените на реальный URL

# URL картинки для раздела документов
DOCUMENTS_IMAGE_URL = None  # Можно указать URL картинки

# Токен бота техподдержки
SUPPORT_BOT_TOKEN = "8523208604:AAF4lLX49wh9ZyvhiRevX7TDBMgI8A1pVYU"
SUPPORT_CHAT_ID = None  # ID чата техподдержки для пересылки сообщений (будет установлен автоматически)

# Настройки Supabase (из .env или значения по умолчанию)
# Используем anon key для подключения
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wntvxdgxzenehfzvorae.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0")

# Инициализация Supabase клиента
supabase: Optional[Client] = None
if SUPABASE_AVAILABLE:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Подключение к Supabase установлено")
    except Exception as e:
        logger.error(f"Ошибка при подключении к Supabase: {e}", exc_info=True)
        supabase = None
        print(f"⚠️ ВНИМАНИЕ: Не удалось подключиться к Supabase: {e}")
        print("Бот будет работать с локальным хранилищем данных")
else:
    logger.warning("Supabase не доступен, используется локальное хранилище")
    print("⚠️ ВНИМАНИЕ: Supabase не установлен. Установите: pip install supabase==2.3.0 realtime==2.3.0")

# Хранилище данных пользователей (кэш, используется как fallback)
user_data_storage: Dict[int, Dict] = {}

# Глобальная переменная для хранения объекта приложения (для перезапуска)
application_instance: Optional[Application] = None

# Хранилище связи пользователей с чатами техподдержки
# Ключ: user_id основного бота, Значение: chat_id в боте техподдержки
user_support_chat_mapping: Dict[int, int] = {}

# Примеры заказов (в реальном приложении это будет из базы данных)
SAMPLE_ORDERS = [
    {
        "id": 1,
        "name": "Латте",
        "image_url": "https://via.placeholder.com/300x300?text=Latte",
        "modifiers": ["1 шот", "whole (молоко цельное)"]
    },
    {
        "id": 2,
        "name": "Капучино",
        "image_url": "https://via.placeholder.com/300x300?text=Cappuccino",
        "modifiers": ["M (350мл)", "Соевое молоко", "Ванильный сироп"]
    },
    {
        "id": 3,
        "name": "Американо",
        "image_url": "https://via.placeholder.com/300x300?text=Americano",
        "modifiers": ["2 шота", "Без сахара"]
    },
    {
        "id": 4,
        "name": "Эспрессо",
        "image_url": "https://via.placeholder.com/300x300?text=Espresso",
        "modifiers": ["1 шот", "Классический"]
    },
    {
        "id": 5,
        "name": "Раф кофе",
        "image_url": "https://via.placeholder.com/300x300?text=Raf",
        "modifiers": ["1 шот", "Сливки", "Ванильный сироп"]
    },
    {
        "id": 6,
        "name": "Флэт Уайт",
        "image_url": "https://via.placeholder.com/300x300?text=Flat+White",
        "modifiers": ["2 шота", "Овсяное молоко"]
    },
]


def get_main_keyboard(user_id: Optional[int] = None):
    """Создаёт основную клавиатуру (динамический URL меню с учётом последней точки)"""
    print(f"\n{'#'*70}")
    print(f"# get_main_keyboard CALLED with user_id={user_id}")
    print(f"{'#'*70}")
    logger.info(f"get_main_keyboard: вызвана с user_id={user_id}")
    
    try:
        web_app_url = build_catalog_url(user_id)
        print(f"# GENERATED URL: {web_app_url}")
        logger.info(f"get_main_keyboard: сформирован URL = {web_app_url}")
    except Exception as e:
        print(f"# ERROR in build_catalog_url: {e}")
        logger.error(f"get_main_keyboard: ошибка в build_catalog_url: {e}")
        web_app_url = WEB_APP_URL
    
    # Проверяем что URL содержит параметры
    if "?" in web_app_url:
        print(f"# SUCCESS: URL contains location parameters!")
        logger.info(f"get_main_keyboard: URL содержит параметры локации!")
    else:
        print(f"# WARNING: URL has NO parameters - will show initial WebApp screen")
        logger.warning(f"get_main_keyboard: URL БЕЗ параметров, будет показан начальный экран WebApp")
    
    print(f"{'#'*70}\n")
    web_app_info = WebAppInfo(url=web_app_url)
    
    keyboard = [
        [InlineKeyboardButton(text="📦 Открыть меню", web_app=web_app_info)],
        [InlineKeyboardButton(text="📜 Мои заказы", callback_data="menu_order_history")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")],
        [InlineKeyboardButton(text="📄 Документы", callback_data="menu_documents")],
        [InlineKeyboardButton(text="💬 Тех поддержка", callback_data="menu_support")],
    ]
    
    return InlineKeyboardMarkup(keyboard)


def build_catalog_url(user_id: Optional[int] = None) -> str:
    """Формирует URL WebApp с учётом последней локации пользователя.

    ИСПРАВЛЕНИЕ: Использует только fragment (hash) для передачи параметров,
    так как это единственный способ, который надёжно работает в Telegram Mini Apps.
    Query string параметры игнорируются Telegram при открытии WebApp.
    """
    web_app_url = WEB_APP_URL
    if not user_id or not supabase:
        logger.debug(f"build_catalog_url: user_id={user_id}, supabase={bool(supabase)} — возвращаю базовый URL")
        return web_app_url

    import urllib.parse
    import base64
    import json

    try:
        logger.info(f"build_catalog_url: получаем контекст локации для user_id={user_id}")
        ctx = get_user_location_context(user_id)
        logger.info(f"build_catalog_url: контекст локации = {ctx}")

        if ctx and ctx.get("location_id"):
            # ⭐ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Передаём telegram_user_id в URL!
            # Это необходимо потому что Telegram.WebApp.initDataUnsafe.user часто null!
            location_data = {
                "action": "open_catalog",
                "telegram_user_id": str(user_id),  # ⭐ ДОБАВЛЕНО: ID пользователя!
                "location_id": ctx["location_id"],
                "latitude": ctx.get("lat"),
                "longitude": ctx.get("lon"),
                "location_name": ctx.get("name")
            }

            # Вариант 1: Передаём через fragment как query string (для совместимости)
            params_str = urllib.parse.urlencode(location_data, doseq=False)

            # Вариант 2: Также добавляем base64 JSON для более сложных фронтендов
            json_str = json.dumps(location_data, ensure_ascii=False)
            b64_data = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')

            # Формируем URL: сначала простые параметры, потом base64 данные
            web_app_url = f"{WEB_APP_URL}#{params_str}&data={b64_data}"

            logger.info(f"build_catalog_url: сформирован URL с параметрами: {web_app_url}")
            print(f"\n{'='*60}")
            print(f"[CATALOG URL] Сформирован URL для пользователя {user_id}:")
            print(f"  telegram_user_id: {user_id}")  # ⭐ ДОБАВЛЕНО
            print(f"  location_id: {location_data.get('location_id')}")
            print(f"  latitude: {location_data.get('latitude')}")
            print(f"  longitude: {location_data.get('longitude')}")
            print(f"  location_name: {location_data.get('location_name')}")
            print(f"  URL: {web_app_url}")
            print(f"  Fragment: {params_str}")
            print(f"  Base64 JSON: {b64_data}")
            print(f"{'='*60}\n")
        else:
            logger.info(f"build_catalog_url: локация не найдена, возвращаю базовый URL")
            print(f"\n[CATALOG URL] Локация не найдена для user_id={user_id}, базовый URL\n")
    except Exception as e:
        logger.error(f"Ошибка в build_catalog_url: {e}", exc_info=True)
        print(f"\n[CATALOG URL ERROR] {e}\n")

    return web_app_url


def get_user_welcome_context(user_id: int) -> Optional[Dict]:
    """Получает контекст для приветствия: имя пользователя и название последней кофейни"""
    if not supabase:
        return None
    
    try:
        # Ищем пользователя
        user_resp = supabase.table("User").select("*").eq("telegramId", user_id).limit(1).execute()
        if not user_resp.data or len(user_resp.data) == 0:
            user_resp = supabase.table("User").select("*").eq("telegram_user_id", user_id).limit(1).execute()
        
        if user_resp.data and len(user_resp.data) > 0:
            user_row = user_resp.data[0]
            user_name = user_row.get("telegramFirstName") or user_row.get("telegramUsername") or "друг"
            preferred_location_id = user_row.get("preferredLocationId")
            
            location_name = None
            if preferred_location_id:
                loc = _fetch_location(preferred_location_id)
                if loc:
                    location_name = loc.get("name")
            
            return {
                "user_name": user_name,
                "location_name": location_name,
            }
    except Exception as e:
        logger.debug(f"Ошибка получения контекста приветствия: {e}")
    
    return None


def build_repeat_order_url(order_id: str, location_id: str) -> str:
    """Формирует URL для повторного заказа с параметрами в hash"""
    import urllib.parse
    import base64
    import json
    
    web_app_url = WEB_APP_URL
    
    # Параметры для передачи в WebApp через hash
    params = {
        "action": "repeat_order",
        "order_id": order_id,
        "location_id": location_id,
    }
    
    # Формируем hash параметры
    params_str = urllib.parse.urlencode(params, doseq=False)
    
    # Также добавляем base64 JSON для надёжности
    json_str = json.dumps(params, ensure_ascii=False)
    b64_data = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')
    
    # Используем hash вместо query параметров (Telegram игнорирует query)
    web_app_url_with_params = f"{web_app_url}#{params_str}&data={b64_data}"
    
    logger.info(f"build_repeat_order_url: order_id={order_id}, location_id={location_id}, URL={web_app_url_with_params}")
    
    return web_app_url_with_params


def get_order_keyboard(order: Dict, order_index: int, total_orders: int, user_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для просмотра заказа"""
    keyboard = []
    
    # Получаем order_id и location_id из заказа
    order_id = str(order.get("id", ""))
    location_id = str(order.get("locationId", "")) or str(order.get("location_id", ""))
    
    # Получаем location объект для геолокации
    location = order.get("location")
    
    if not location_id and location:
        # Пробуем получить location_id из объекта location
        if isinstance(location, dict):
            location_id = str(location.get("id", "")) or str(location.get("locationId", ""))
    
    # Если location_id всё ещё нет, пробуем получить из контекста пользователя
    if not location_id and user_id:
        try:
            ctx = get_user_location_context(user_id)
            if ctx and ctx.get("location_id"):
                location_id = ctx["location_id"]
        except:
            pass
    
    if order_id and location_id:
        # Формируем URL для повторного заказа
        web_app_url_with_params = build_repeat_order_url(order_id, location_id)
        web_app_info = WebAppInfo(url=web_app_url_with_params)
        
        # Кнопка "Повторить заказ" - открывает WebApp с данными заказа
        keyboard.append([
            InlineKeyboardButton(
                text="🔄 Повторить",
                web_app=web_app_info
            )
        ])
    else:
        logger.warning(f"Не удалось сформировать URL для повторного заказа: order_id={order_id}, location_id={location_id}")
    
    # Кнопка для просмотра геолокации на карте, если есть
    # Используем геолокацию из заказа или из профиля пользователя
    if not location or not isinstance(location, dict) or not location.get("latitude") or not location.get("longitude"):
        # Если в заказе нет геолокации, пробуем получить из профиля
        if user_id:
            user_data = get_user_data(user_id)
            if user_data and user_data.get("location"):
                location = user_data["location"]
    
    if location and isinstance(location, dict) and location.get("latitude") and location.get("longitude"):
        lat = location.get("latitude")
        lon = location.get("longitude")
        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        keyboard.append([
            InlineKeyboardButton(
                text="📍 Открыть на карте",
                url=map_url
            )
        ])
    
    # Кнопки навигации убраны, так как теперь показываем все заказы списком
    # Но оставляем для совместимости, если понадобится
    
    return InlineKeyboardMarkup(keyboard)


def format_order_message(order: Dict, order_index: int, total_orders: int) -> str:
    """Форматирует сообщение с информацией о заказе"""
    message = f"📜 Мои заказы ({order_index + 1} из {total_orders})\n\n"
    message += f"🥤 {order.get('name', 'Заказ')}\n\n"
    
    # Добавляем модификаторы, если они есть
    modifiers = order.get("modifiers", [])
    if modifiers and len(modifiers) > 0:
        message += "Модификаторы:\n"
        modifiers_text = "\n".join([f"  • {mod}" for mod in modifiers])
        message += modifiers_text + "\n\n"
    
    # Добавляем информацию о статусе и сумме, если есть
    if order.get("status"):
        status_emoji = "✅" if order.get("status") in ["paid", "completed", "PAID", "COMPLETED"] else "⏳"
        message += f"{status_emoji} Статус: {order.get('status')}\n"
    
    if order.get("total"):
        message += f"💰 Сумма: {order.get('total')} ₽\n"
    
    if order.get("createdAt"):
        message += f"📅 Дата: {order.get('createdAt')}\n"
    
    # Добавляем геолокацию, если есть
    location = order.get("location")
    if location and location.get("latitude") and location.get("longitude"):
        lat = location.get("latitude")
        lon = location.get("longitude")
        message += f"\n📍 Геолокация:\n"
        message += f"  Широта: {lat}\n"
        message += f"  Долгота: {lon}\n"
        # Ссылка на карту
        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        message += f"  [Открыть на карте]({map_url})"
    
    # Добавляем адрес, если есть
    if order.get("address"):
        message += f"\n🏠 Адрес: {order.get('address')}\n"
    
    # Добавляем способ оплаты, если есть
    if order.get("paymentMethod"):
        message += f"💳 Способ оплаты: {order.get('paymentMethod')}\n"
    
    return message


def get_user_from_db(user_id: int) -> Optional[Dict]:
    """Получает данные пользователя из Supabase по telegramId или telegram_user_id"""
    if not supabase:
        return None
    
    try:
        # Ищем пользователя по telegramId (Prisma схема)
        response = supabase.table("User").select("*").eq("telegramId", user_id).limit(1).execute()
        
        # Fallback: если не нашли по telegramId, пробуем telegram_user_id
        if not response.data or len(response.data) == 0:
            response = supabase.table("User").select("*").eq("telegram_user_id", user_id).limit(1).execute()
        
        if response and response.data and len(response.data) > 0:
            user = response.data[0]
            return {
                "telegram_id": user.get("telegramId"),
                "id": user.get("id"),  # UUID из таблицы User
                "first_name": user.get("telegramFirstName") or user.get("telegramLastName") or user.get("first_name"),
                "username": user.get("telegramUsername") or user.get("username"),
                "language_code": user.get("telegramLanguageCode") or user.get("language_code"),
                "photo_url": user.get("telegramPhotoUrl") or user.get("photo_url"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "totalOrdersAmount": user.get("totalOrdersAmount", 0),
                "totalOrdersCount": user.get("totalOrdersCount", 0),
                "lastOrderAt": user.get("lastOrderAt"),
                "preferredLocationId": user.get("preferredLocationId"),
            }
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя из БД: {e}", exc_info=True)
    return None


def get_user_location_context(user_id: int) -> Optional[Dict]:
    """Определяет последнюю локацию пользователя для открытия меню"""
    if not supabase:
        logger.warning("get_user_location_context: supabase не инициализирован")
        return None
    
    user_uuid = None
    preferred_location_id = None
    
    try:
        logger.info(f"get_user_location_context: ищем пользователя {user_id}")
        
        # Пробуем найти пользователя по telegramId (Prisma схема)
        user_resp = supabase.table("User").select("*").eq("telegramId", user_id).limit(1).execute()
        logger.info(f"get_user_location_context: поиск по telegramId, результат: {len(user_resp.data) if user_resp.data else 0} записей")
        
        # Fallback: если не нашли, пробуем telegram_user_id
        if not user_resp.data or len(user_resp.data) == 0:
            user_resp = supabase.table("User").select("*").eq("telegram_user_id", user_id).limit(1).execute()
            logger.info(f"get_user_location_context: поиск по telegram_user_id, результат: {len(user_resp.data) if user_resp.data else 0} записей")
        
        if user_resp.data and len(user_resp.data) > 0:
            user_row = user_resp.data[0]
            user_uuid = user_row.get("id")
            preferred_location_id = user_row.get("preferredLocationId") or user_row.get("preferred_location_id")
            logger.info(f"get_user_location_context: найден пользователь {user_id}: UUID={user_uuid}, preferredLocationId={preferred_location_id}")
        else:
            logger.warning(f"get_user_location_context: пользователь {user_id} не найден в БД")
    except Exception as e:
        logger.error(f"get_user_location_context: ошибка при поиске пользователя: {e}", exc_info=True)
    
    # Если есть предпочтительная локация — используем её
    if preferred_location_id:
        logger.info(f"get_user_location_context: используем preferredLocationId={preferred_location_id}")
        loc = _fetch_location(preferred_location_id)
        if loc:
            logger.info(f"get_user_location_context: локация найдена: {loc}")
            return loc
        else:
            logger.warning(f"get_user_location_context: не удалось получить данные локации {preferred_location_id}")
    
    # Иначе пробуем взять локацию из последнего оплаченного/завершённого заказа
    if user_uuid:
        logger.info(f"get_user_location_context: ищем заказы пользователя UUID={user_uuid}")
        payment_statuses = ["succeeded", "paid", "PAID", "SUCCEEDED"]
        order_statuses = ["paid", "completed", "ready", "PAID", "COMPLETED", "READY"]
        order_fields = ["createdAt", "created_at"]
        
        location_id = None
        
        for order_field in order_fields:
            if location_id:
                break
            for status in payment_statuses:
                try:
                    resp = supabase.table("Order").select("id, locationId").eq("userId", user_uuid).eq("paymentStatus", status).order(order_field, desc=True).limit(1).execute()
                    if resp.data:
                        location_id = resp.data[0].get("locationId")
                        logger.info(f"get_user_location_context: найден заказ с paymentStatus={status}, locationId={location_id}")
                        break
                except Exception as e:
                    logger.debug(f"Ошибка при поиске заказа по paymentStatus={status}: {e}")
            
            if location_id:
                break
            
            for status in order_statuses:
                try:
                    resp = supabase.table("Order").select("id, locationId").eq("userId", user_uuid).eq("status", status).order(order_field, desc=True).limit(1).execute()
                    if resp.data:
                        location_id = resp.data[0].get("locationId")
                        logger.info(f"get_user_location_context: найден заказ с status={status}, locationId={location_id}")
                        break
                except Exception as e:
                    logger.debug(f"Ошибка при поиске заказа по status={status}: {e}")
        
        # Если так и не нашли — берем просто последний заказ
        if not location_id:
            logger.info("get_user_location_context: не нашли оплаченных заказов, ищем любой последний")
            for order_field in order_fields:
                try:
                    resp = supabase.table("Order").select("id, locationId").eq("userId", user_uuid).order(order_field, desc=True).limit(1).execute()
                    if resp.data:
                        location_id = resp.data[0].get("locationId")
                        logger.info(f"get_user_location_context: найден последний заказ, locationId={location_id}")
                        break
                except Exception as e:
                    logger.debug(f"Ошибка при поиске последнего заказа: {e}")
        
        if location_id:
            loc = _fetch_location(location_id)
            if loc:
                logger.info(f"get_user_location_context: локация из заказа найдена: {loc}")
                return loc
            else:
                logger.warning(f"get_user_location_context: не удалось получить данные локации {location_id}")
        else:
            logger.info("get_user_location_context: заказы не найдены")
    else:
        logger.warning("get_user_location_context: user_uuid не определён, не можем искать заказы")
    
    logger.info("get_user_location_context: локация не найдена, возвращаем None")
    return None


def _fetch_location(location_id: str) -> Optional[Dict]:
    """Возвращает данные локации: id, lat/lon, name"""
    try:
        logger.info(f"_fetch_location: получаем данные локации {location_id}")
        resp = supabase.table("Location").select("id, latitude, longitude, name").eq("id", location_id).limit(1).execute()
        if resp.data and len(resp.data) > 0:
            row = resp.data[0]
            lat = row.get("latitude")
            lon = row.get("longitude")
            name = row.get("name")
            logger.info(f"_fetch_location: найдена локация '{name}' (lat={lat}, lon={lon})")
            return {
                "location_id": row.get("id"),
                "lat": lat,
                "lon": lon,
                "name": name,
            }
        else:
            logger.warning(f"_fetch_location: локация {location_id} не найдена в таблице Location")
    except Exception as e:
        logger.error(f"_fetch_location: ошибка при получении локации {location_id}: {e}", exc_info=True)
    return None


def save_user_to_db(user_id: int, user_data: Dict, update_user: Optional[Dict] = None) -> bool:
    """Сохраняет или обновляет пользователя в Supabase по telegramId"""
    if not supabase:
        logger.warning("Supabase клиент не инициализирован")
        return False
    
    try:
        # Подготавливаем данные для сохранения
        first_name = update_user.get("first_name") if update_user else user_data.get("first_name")
        username = update_user.get("username") if update_user else user_data.get("username")
        language_code = update_user.get("language_code") if update_user else user_data.get("language_code")
        
        # Данные для записи (оба поля для совместимости)
        db_data = {
            "telegramId": user_id,  # Prisma схема
            "telegram_user_id": user_id,  # Альтернативное поле в БД
        }
        
        # Добавляем имя
        if first_name:
            db_data["telegramFirstName"] = first_name
            db_data["first_name"] = first_name
        
        # Добавляем username
        if username:
            db_data["telegramUsername"] = username
            db_data["username"] = username
        
        # Добавляем язык
        if language_code:
            db_data["telegramLanguageCode"] = language_code
            db_data["language_code"] = language_code
        
        # Ищем пользователя по telegramId или telegram_user_id
        existing = None
        found_by_field = None
        try:
            existing = supabase.table("User").select("id").eq("telegramId", user_id).execute()
            if existing.data and len(existing.data) > 0:
                found_by_field = "telegramId"
            else:
                existing = supabase.table("User").select("id").eq("telegram_user_id", user_id).execute()
                if existing.data and len(existing.data) > 0:
                    found_by_field = "telegram_user_id"
        except Exception as e:
            logger.debug(f"Ошибка при поиске пользователя: {e}")
        
        if found_by_field and existing and existing.data:
            user_db_id = existing.data[0].get("id")
            logger.info(f"Найден пользователь по {found_by_field} {user_id}, UUID в БД: {user_db_id}")
            
            # Обновляем существующего пользователя
            result = supabase.table("User").update(db_data).eq(found_by_field, user_id).execute()
            logger.info(f"Пользователь {user_db_id} успешно обновлен")
            return True
        
        # Пользователя нет - создаём нового
        db_data["totalOrdersAmount"] = 0
        db_data["totalOrdersCount"] = 0
        
        logger.info(f"Создание нового пользователя (telegramId: {user_id}, имя: {first_name}, username: {username})")
        result = supabase.table("User").insert(db_data).execute()
        logger.info(f"Новый пользователь успешно создан: {result.data if result.data else 'данные не возвращены'}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя в БД: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def ensure_user_registered(update: Update) -> None:
    """Автоматически регистрирует пользователя при первом взаимодействии"""
    if not update.effective_user:
        logger.warning("ensure_user_registered: update.effective_user отсутствует")
        return
    
    user = update.effective_user
    user_id = user.id
    
    logger.info(f"Проверка регистрации пользователя {user_id} (имя: {user.first_name}, username: {user.username})")
    
    # Проверяем, есть ли пользователь в БД
    if not supabase:
        logger.warning("Supabase клиент не инициализирован, регистрация невозможна")
        return
    
    try:
        # Ищем пользователя по telegramId или telegram_user_id
        existing = None
        try:
            existing = supabase.table("User").select("id").eq("telegramId", user_id).execute()
            if existing.data and len(existing.data) > 0:
                logger.info(f"Пользователь {user_id} найден в БД по telegramId")
                return
            
            # Fallback: пробуем telegram_user_id
            existing = supabase.table("User").select("id").eq("telegram_user_id", user_id).execute()
            if existing.data and len(existing.data) > 0:
                logger.info(f"Пользователь {user_id} найден в БД по telegram_user_id")
                return
        except Exception as e:
            logger.debug(f"Ошибка при поиске пользователя: {e}")
        
        # Пользователя нет - создаём
        logger.info(f"Пользователь {user_id} не найден в БД, создаём новую запись")
        success = save_user_to_db(user_id, {}, {
            "first_name": user.first_name,
            "username": user.username,
            "language_code": user.language_code
        })
        
        if success:
            logger.info(f"✅ Автоматически зарегистрирован пользователь {user_id}: {user.first_name}")
        else:
            logger.error(f"❌ Не удалось зарегистрировать пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка при проверке/регистрации пользователя: {e}", exc_info=True)
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


def save_location_to_db(user_id: int, latitude: float, longitude: float) -> bool:
    """Сохраняет геолокацию пользователя в Supabase по telegramId или telegram_user_id"""
    if not supabase:
        return False
    
    try:
        update_data = {
            "latitude": latitude,
            "longitude": longitude,
        }
        
        # Сначала пробуем обновить по telegramId
        try:
            result = supabase.table("User").update(update_data).eq("telegramId", user_id).execute()
            if result.data and len(result.data) > 0:
                logger.info(f"Геолокация сохранена для пользователя {user_id} (telegramId): {latitude}, {longitude}")
                return True
        except:
            pass
        
        # Fallback: пробуем telegram_user_id
        try:
            result = supabase.table("User").update(update_data).eq("telegram_user_id", user_id).execute()
            if result.data and len(result.data) > 0:
                logger.info(f"Геолокация сохранена для пользователя {user_id} (telegram_user_id): {latitude}, {longitude}")
                return True
        except:
            pass
        
        logger.warning(f"Не удалось сохранить геолокацию: пользователь {user_id} не найден")
        return False
    except Exception as e:
        logger.error(f"Ошибка при сохранении геолокации в БД: {e}", exc_info=True)
        return False


def get_last_order_from_db(user_id: int) -> Optional[Dict]:
    """Получает последний оплаченный заказ пользователя из Supabase"""
    if not supabase:
        return None
    
    try:
        # Пробуем найти оплаченный заказ
        status_variants = ["paid", "completed", "PAID", "COMPLETED"]
        for status in status_variants:
            try:
                response = supabase.table("Order").select("*").eq("userId", user_id).eq("status", status).order("createdAt", desc=True).limit(1).execute()
                if response.data and len(response.data) > 0:
                    order = response.data[0]
                    return {
                        "id": order.get("id"),
                        "name": f"Заказ #{order.get('id')}",
                        "modifiers": [],
                        "image_url": "https://via.placeholder.com/300x300?text=Order",
                        "created_at": order.get("createdAt")
                    }
            except:
                continue
        
        # Если не нашли оплаченный, берем последний
        response = supabase.table("Order").select("*").eq("userId", user_id).order("createdAt", desc=True).limit(1).execute()
        if response.data and len(response.data) > 0:
            order = response.data[0]
            return {
                "id": order.get("id"),
                "name": f"Заказ #{order.get('id')}",
                "modifiers": [],
                "image_url": "https://via.placeholder.com/300x300?text=Order",
                "created_at": order.get("createdAt")
            }
    except Exception as e:
        logger.error(f"Ошибка при получении последнего заказа из БД: {e}")
    return None


def save_order_to_db(user_id: int, order_data: Dict) -> bool:
    """Сохраняет заказ в Supabase (если нужно создать запись в Order)"""
    if not supabase:
        return False
    
    try:
        # Если заказ уже существует в Order таблице, просто возвращаем True
        # Иначе можно создать запись, но структура Order может быть сложной
        # Пока просто логируем
        logger.info(f"Заказ {order_data.get('id')} для пользователя {user_id} получен из WebApp")
        return True
    except Exception as e:
        logger.error(f"Ошибка при сохранении заказа в БД: {e}")
        return False


def get_user_data(user_id: int) -> Dict:
    """Получает данные пользователя (из Supabase или кэша)"""
    # Сначала пытаемся получить из Supabase
    if supabase:
        db_user = get_user_from_db(user_id)
        if db_user:
            # Обновляем кэш
            user_data_storage[user_id] = db_user
            return db_user
    
    # Если нет подключения к БД или пользователь не найден, используем кэш
    if user_id not in user_data_storage:
        user_data_storage[user_id] = {
            "email": None,
            "points": 0,
            "referral_code": f"ref_{user_id}",
            "location": None,  # {"latitude": float, "longitude": float}
            "orders": [],  # Список заказов пользователя
        }
        # Пытаемся сохранить нового пользователя в БД
        if supabase:
            save_user_to_db(user_id, user_data_storage[user_id])
    
    return user_data_storage[user_id]


def get_profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для профиля"""
    web_app_info = WebAppInfo(url=WEB_APP_URL)
    user_data = get_user_data(user_id)
    
    keyboard = []
    
    # Промо-блок 1: "Любой напиток за 1₽" (чёрный блок)
    keyboard.append([
        InlineKeyboardButton(
            text="Любой напиток за 1₽\nкогда нужно исполнить это...",
            callback_data="promo_1_rub"
        )
    ])
    
    # Промо-блок 2: "Пригласить друга" (белый блок)
    keyboard.append([
        InlineKeyboardButton(
            text="Пригласить друга",
            callback_data="referral_invite"
        )
    ])
    
    # Промо-блок 3: "Ты любишь, мы улучшаем" (чёрный блок)
    keyboard.append([
        InlineKeyboardButton(
            text="Ты любишь, мы улучшаем\nПоделись своим мнением о нас\nчтобы получить +200 баллов",
            callback_data="feedback_survey"
        )
    ])
    
    # Информационные кнопки
    keyboard.append([
        InlineKeyboardButton(
            text="Правила акции",
            callback_data="promo_rules"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Другие промыши по ссылке",
            url=PROMO_LINK_URL
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Скачать квитанцию для юриков",
            callback_data="download_receipt"
        )
    ])
    
    # Навигация
    keyboard.append([
        InlineKeyboardButton(
            text="<< Главное меню",
            callback_data="back_to_menu"
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_support_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для раздела техподдержки"""
    keyboard = []
    
    # Кнопка "Главное меню"
    keyboard.append([
        InlineKeyboardButton(
            text="<< Главное меню",
            callback_data="back_to_menu"
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_documents_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для раздела документов"""
    keyboard = []
    
    # Юридические документы
    keyboard.append([
        InlineKeyboardButton(
            text="Политика обработки данных",
            url=f"{DOCUMENTS_BASE_URL}/privacy"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Пользовательское соглашение",
            url=f"{DOCUMENTS_BASE_URL}/terms"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Публичная оферта",
            url=f"{DOCUMENTS_BASE_URL}/offer"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Полные правила акций",
            url=f"{DOCUMENTS_BASE_URL}/promo-rules"
        )
    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="Калорийность состав",
            url=f"{DOCUMENTS_BASE_URL}/nutrition"
        )
    ])
    
    # Программа благодарности
    keyboard.append([
        InlineKeyboardButton(
            text="Программа благодарности",
            callback_data="doc_gratitude_program"
        )
    ])
    
    # Навигация
    keyboard.append([
        InlineKeyboardButton(
            text="<< Главное меню",
            callback_data="back_to_menu"
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


def format_profile_message(user, user_data: Dict) -> str:
    """Форматирует сообщение профиля"""
    email_text = user_data.get("email") or "Не указана"
    points = user_data.get("points", 0)
    
    message = (
        f"👤 Профиль\n\n"
        f"- Имя: {user.first_name or 'Не указано'}\n"
        f"- Почта: {email_text}\n"
        f"- Баллы: {points}"
    )
    
    return message


async def restart_bot(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перезапускает бота"""
    try:
        logger.info("Инициирован перезапуск бота...")
        # Завершаем текущий процесс и перезапускаем скрипт
        python = sys.executable
        os.execv(python, [python] + sys.argv)
    except Exception as e:
        logger.error(f"Ошибка при перезапуске бота: {e}", exc_info=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Команда /start — отправляет приветствие с картинкой и меню.
    Обрабатывает реферальные ссылки.
    При выполнении команды перезапускает бота.
    """
    try:
        if not update.message:
            logger.warning("Update не содержит message")
            return

        user_id = update.effective_user.id
        user = update.effective_user
        
        # Сохраняем/обновляем пользователя в БД
        user_data = get_user_data(user_id)
        save_user_to_db(user_id, user_data, {
            "first_name": user.first_name,
            "username": user.username
        })
        
        # Проверяем реферальный код
        if context.args and len(context.args) > 0:
            referral_code = context.args[0]
            if referral_code.startswith("ref_"):
                # Пользователь пришёл по реферальной ссылке
                referrer_id = int(referral_code.split("_")[1])
                
                # Проверяем, что это новый пользователь (не регистрировался ранее)
                if user_id not in user_data_storage or user_data_storage[user_id].get("points", 0) == 0:
                    # Начисляем баллы рефереру
                    referrer_data = get_user_data(referrer_id)
                    referrer_data["points"] = referrer_data.get("points", 0) + 200
                    
                    # Начисляем баллы новому пользователю
                    user_data["points"] = 100
                    
                    await update.message.reply_text(
                        f"🎉 Добро пожаловать!\n\n"
                        f"Вы зарегистрировались по реферальной ссылке!\n"
                        f"Вам начислено: +100 баллов\n\n"
                        f"Спасибо, что привели друга!",
                    )
                    logger.info(f"Новый пользователь {user_id} зарегистрирован по реферальной ссылке от {referrer_id}")

        # Отправляем картинку/баннер, если указан URL
        if BANNER_IMAGE_URL:
            try:
                await update.message.reply_photo(
                    photo=BANNER_IMAGE_URL,
                    caption="",
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить картинку: {e}")

        # Получаем контекст для персонализированного приветствия
        welcome_ctx = get_user_welcome_context(user_id)
        
        # Формируем персонализированное приветствие
        if welcome_ctx and welcome_ctx.get("user_name"):
            user_name = welcome_ctx.get("user_name")
            location_name = welcome_ctx.get("location_name")
            
            if location_name:
                welcome_text = (
                    f"Привет, {user_name}! 👋\n\n"
                    f"📍 Твоя кофейня: {location_name}\n\n"
                    "Выбери действие:\n\n"
                    "📦 Открыть меню — сразу в твою кофейню\n"
                    "📜 Мои заказы — твои предыдущие заказы\n"
                    "👤 Профиль — личные данные\n"
                    "📄 Документы — чеки и документы\n"
                    "💬 Тех поддержка — связь с поддержкой"
                )
            else:
                welcome_text = (
                    f"Привет, {user_name}! 👋\n\n"
                    "Выбери действие:\n\n"
                    "📦 Открыть меню — просмотр товаров\n"
                    "📜 Мои заказы — твои предыдущие заказы\n"
                    "👤 Профиль — личные данные\n"
                    "📄 Документы — чеки и документы\n"
                    "💬 Тех поддержка — связь с поддержкой"
                )
        else:
            welcome_text = (
                "Привет! Выбери действие:\n\n"
                "📦 Открыть меню — просмотр товаров\n"
                "📜 Мои заказы — твои предыдущие заказы\n"
                "👤 Профиль — личные данные\n"
                "📄 Документы — чеки и документы\n"
                "💬 Тех поддержка — связь с поддержкой"
            )

        # Отправляем приветственное сообщение с клавиатурой
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_keyboard(user_id),
        )
        logger.info(f"Отправлено приветствие пользователю {user_id}")
        
        # Перезапускаем бота после отправки приветствия
        logger.info("Выполняется перезапуск бота по команде /start")
        # Используем asyncio для задержки перед перезапуском, чтобы сообщение успело отправиться
        import asyncio
        await asyncio.sleep(1)  # Небольшая задержка для отправки сообщения
        await restart_bot(context)
    except Exception as e:
        logger.error(f"Ошибка в функции start: {e}", exc_info=True)


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик данных из WebApp"""
    try:
        # Автоматическая регистрация пользователя
        await ensure_user_registered(update)
        
        if not update.message or not update.message.web_app_data:
            return
        
        user_id = update.effective_user.id
        web_app_data = update.message.web_app_data
        
        # Парсим данные из WebApp (ожидаем JSON)
        import json
        try:
            data = json.loads(web_app_data.data)
            
            # Обрабатываем геолокацию, если она есть в данных
            if "location" in data:
                location_data = data["location"]
                latitude = float(location_data.get("latitude", 0))
                longitude = float(location_data.get("longitude", 0))
                
                # Сохраняем в Supabase
                save_location_to_db(user_id, latitude, longitude)
                
                # Обновляем кэш
                user_data = get_user_data(user_id)
                user_data["location"] = {
                    "latitude": latitude,
                    "longitude": longitude
                }
                logger.info(f"Сохранена геолокация из WebApp для пользователя {user_id}")
                
                await update.message.reply_text(
                    "✅ Геолокация сохранена! Теперь вы можете быстро повторить заказ.",
                    reply_markup=get_main_keyboard(user_id),
                )
            
            # Обрабатываем данные заказа, если они есть
            if "order" in data:
                order_data = data["order"]
                
                # Сохраняем заказ в Supabase
                save_order_to_db(user_id, order_data)
                
                # Обновляем кэш
                user_data = get_user_data(user_id)
                if "orders" not in user_data:
                    user_data["orders"] = []
                user_data["orders"].append(order_data)
                logger.info(f"Сохранён заказ из WebApp для пользователя {user_id}")
                
        except json.JSONDecodeError as e:
            logger.warning(f"Не удалось распарсить данные WebApp: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке данных WebApp: {e}", exc_info=True)
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике WebApp данных: {e}", exc_info=True)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (только для техподдержки и фидбека)"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        
        # Обрабатываем геолокацию, если она отправлена
        if update.message.location:
            location = update.message.location
            
            # Сохраняем в Supabase
            save_location_to_db(user_id, location.latitude, location.longitude)
            
            # Обновляем кэш
            user_data = get_user_data(user_id)
            user_data["location"] = {
                "latitude": location.latitude,
                "longitude": location.longitude
            }
            logger.info(f"Сохранена геолокация для пользователя {user_id}: {location.latitude}, {location.longitude}")
            
            await update.message.reply_text(
                "✅ Геолокация сохранена! Теперь вы можете быстро повторить заказ.",
                reply_markup=get_main_keyboard(user_id),
            )
            return

        if not update.message.text:
            return

        # Проверяем, находится ли пользователь в режиме техподдержки
        if context.user_data.get("in_support_mode"):
            await handle_support_message(update, context)
        # Проверяем, ожидается ли фидбек
        elif context.user_data.get("waiting_feedback"):
            # Пользователь отправляет фидбек
            user_data = get_user_data(user_id)
            user_data["points"] = user_data.get("points", 0) + 200
            context.user_data["waiting_feedback"] = False
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
            ]])
            
            await update.message.reply_text(
                "✅ Спасибо за ваш отзыв!\n\n"
                "Вам начислено: +200 баллов\n\n"
                "Ваше мнение очень важно для нас!",
                reply_markup=keyboard,
            )
            logger.info(f"Пользователь {user_id} отправил фидбек и получил +200 баллов")
        else:
            # Для любых других сообщений показываем главное меню
            await update.message.reply_text(
                "Используйте кнопки меню для навигации.",
                reply_markup=get_main_keyboard(user_id),
            )

        logger.info(f"Обработано сообщение от пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике сообщений: {e}", exc_info=True)


async def _process_orders(orders_data: List[Dict], user_location: Optional[Dict]) -> List[Dict]:
    """Обрабатывает данные заказов и добавляет информацию о продуктах"""
    orders = []
    
    for order in orders_data:
        order_id = order.get("id")
        
        # Получаем данные о продуктах из OrderItem
        order_name = f"Заказ #{str(order_id)[:8]}"
        modifiers_list = []
        
        try:
            # Получаем OrderItem для этого заказа
            items_response = supabase.table("OrderItem").select("*").eq("orderId", order_id).execute()
            if items_response.data:
                product_names = []
                for item in items_response.data:
                    try:
                        product_id = item.get("productId") or item.get("product_id")
                        if product_id:
                            product = supabase.table("Product").select("name").eq("id", product_id).limit(1).execute()
                            if product.data:
                                product_names.append(product.data[0].get("name", ""))
                        
                        # Получаем модификаторы для этого OrderItem
                        item_id = item.get("id")
                        if item_id:
                            modifiers_response = supabase.table("OrderItemModifier").select("*").eq("orderItemId", item_id).execute()
                            if modifiers_response.data:
                                for mod_item in modifiers_response.data:
                                    modifier_id = mod_item.get("modifierOptionId") or mod_item.get("modifier_option_id")
                                    if modifier_id:
                                        try:
                                            modifier = supabase.table("ModifierOption").select("name").eq("id", modifier_id).limit(1).execute()
                                            if modifier.data:
                                                modifiers_list.append(modifier.data[0].get("name", ""))
                                        except:
                                            pass
                    except Exception as e:
                        logger.debug(f"Ошибка при получении данных продукта: {e}")
                        pass
                
                if product_names:
                    order_name = ", ".join(product_names[:3])
                    if len(product_names) > 3:
                        order_name += f" и ещё {len(product_names) - 3}"
        except Exception as e:
            logger.debug(f"Ошибка при получении OrderItem: {e}")
            pass
        
        orders.append({
            "id": str(order_id),
            "name": order_name,
            "modifiers": modifiers_list if modifiers_list else [],
            "image_url": "https://via.placeholder.com/300x300?text=Order",
            "status": order.get("status"),
            "paymentStatus": order.get("paymentStatus"),
            "createdAt": order.get("createdAt") or order.get("created_at"),
            "total": order.get("totalAmount") or order.get("total") or 0,
            "locationId": order.get("locationId") or order.get("location_id"),  # Добавляем locationId
            "location": user_location,
            "address": order.get("address") or order.get("deliveryAddress") or order.get("delivery_address"),
            "phone": order.get("phone") or order.get("phoneNumber") or order.get("phone_number"),
            "paymentMethod": order.get("paymentMethod") or order.get("payment_method"),
        })
    
    return orders


async def get_user_orders_from_db(user_id: int) -> List[Dict]:
    """Получает последние 3 оплаченных заказа пользователя из Supabase с геолокацией"""
    if not supabase:
        logger.warning("Supabase не подключен, возвращаю пустой список заказов")
        return []
    
    try:
        # ШАГ 1: Находим пользователя в таблице User по telegramId или telegram_user_id и получаем его UUID
        user_uuid = None
        try:
            user_response = supabase.table("User").select("id").eq("telegramId", user_id).execute()
            if user_response.data and len(user_response.data) > 0:
                user_uuid = user_response.data[0].get("id")
                logger.info(f"Найден пользователь: telegramId={user_id}, UUID={user_uuid}")
            else:
                # Fallback: пробуем telegram_user_id
                user_response = supabase.table("User").select("id").eq("telegram_user_id", user_id).execute()
                if user_response.data and len(user_response.data) > 0:
                    user_uuid = user_response.data[0].get("id")
                    logger.info(f"Найден пользователь: telegram_user_id={user_id}, UUID={user_uuid}")
                else:
                    logger.warning(f"Пользователь с telegramId/telegram_user_id={user_id} не найден в таблице User")
                    return []
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователя: {e}", exc_info=True)
            return []
        
        if not user_uuid:
            logger.warning(f"Не удалось получить UUID пользователя для user_id={user_id}")
            return []
        
        # ШАГ 2: Получаем геолокацию пользователя
        user_location = None
        try:
            # Пробуем разные варианты названий полей для геолокации
            location_fields = ["latitude", "location_latitude", "locationLatitude"]
            lon_fields = ["longitude", "location_longitude", "locationLongitude"]
            
            # Получаем данные пользователя (уже знаем что он существует)
            user_response = supabase.table("User").select("*").eq("id", user_uuid).execute()
            if user_response.data and len(user_response.data) > 0:
                user_data = user_response.data[0]
                # Пробуем найти геолокацию в разных полях
                lat = None
                lon = None
                for lat_field in location_fields:
                    if user_data.get(lat_field):
                        lat = user_data.get(lat_field)
                        break
                for lon_field in lon_fields:
                    if user_data.get(lon_field):
                        lon = user_data.get(lon_field)
                        break
                
                if lat and lon:
                    user_location = {
                        "latitude": lat,
                        "longitude": lon
                    }
                    logger.info(f"Получена геолокация пользователя {user_id}: {lat}, {lon}")
        except Exception as e:
            logger.debug(f"Ошибка при получении геолокации пользователя: {e}")
        
        # ШАГ 3: Ищем заказы по userId (UUID из User.id)
        orders = []
        
        # Пробуем разные варианты названий полей для сортировки
        order_by_fields = ["createdAt", "created_at"]
        
        # Пробуем найти по статусу оплаты (paymentStatus) или статусу (status)
        status_variants = ["paid", "completed", "PAID", "COMPLETED", "оплачен", "Оплачен"]
        
        for order_field in order_by_fields:
            # Сначала пробуем по paymentStatus
            for status in status_variants:
                try:
                    response = supabase.table("Order").select("*").eq("userId", user_uuid).eq("paymentStatus", status).order(order_field, desc=True).limit(3).execute()
                    if response.data and len(response.data) > 0:
                        orders = await _process_orders(response.data, user_location)
                        if orders:
                            logger.info(f"Найдено {len(orders)} заказов по paymentStatus={status}")
                            break
                except Exception as e:
                    logger.debug(f"Ошибка при запросе по paymentStatus={status}: {e}")
                    continue
            
            if orders:
                break
            
            # Если не нашли по paymentStatus, пробуем по status
            for status in status_variants:
                try:
                    response = supabase.table("Order").select("*").eq("userId", user_uuid).eq("status", status).order(order_field, desc=True).limit(3).execute()
                    if response.data and len(response.data) > 0:
                        orders = await _process_orders(response.data, user_location)
                        if orders:
                            logger.info(f"Найдено {len(orders)} заказов по status={status}")
                            break
                except Exception as e:
                    logger.debug(f"Ошибка при запросе по status={status}: {e}")
                    continue
            
            if orders:
                break
        
        # Если не нашли по статусу, берем последние 3 заказа без фильтра по статусу
        if not orders:
            for order_field in order_by_fields:
                try:
                    response = supabase.table("Order").select("*").eq("userId", user_uuid).order(order_field, desc=True).limit(3).execute()
                    if response.data and len(response.data) > 0:
                        orders = await _process_orders(response.data, user_location)
                        if orders:
                            logger.info(f"Найдено {len(orders)} заказов без фильтра по статусу")
                            break
                except Exception as e:
                    logger.debug(f"Ошибка при получении последних заказов: {e}")
                    continue
        
        logger.info(f"Получено {len(orders)} заказов из БД для пользователя {user_id} (UUID: {user_uuid})")
        return orders
    except Exception as e:
        logger.error(f"Ошибка при получении заказов из БД: {e}", exc_info=True)
        return []


async def show_order_history(update: Update, context: ContextTypes.DEFAULT_TYPE, order_index: int = 0) -> None:
    """Показывает последние 3 заказа с кнопкой Повторить под каждым"""
    try:
        user_id = update.effective_user.id if update.effective_user else None
        
        if not user_id:
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
            ]])
            if update.message:
                await update.message.reply_text(
                    "Ошибка: не удалось определить пользователя.",
                    reply_markup=keyboard,
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    "Ошибка: не удалось определить пользователя.",
                    reply_markup=keyboard,
                )
                await update.callback_query.answer()
            return
        
        # Получаем заказы из Supabase (только из БД, без fallback)
        all_orders = await get_user_orders_from_db(user_id)
        
        # Берем последние 3 заказа
        orders = all_orders[:3]
        total_orders = len(orders)
        
        if total_orders == 0:
            # Если нет заказов, показываем сообщение
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
            ]])
            if update.message:
                await update.message.reply_text(
                    "📜 Мои заказы\n\nУ вас пока нет заказов.",
                    reply_markup=keyboard,
                )
            elif update.callback_query:
                await update.callback_query.message.reply_text(
                    "📜 Мои заказы\n\nУ вас пока нет заказов.",
                    reply_markup=keyboard,
                )
                await update.callback_query.answer()
            return
        
        # Формируем сообщение со списком заказов
        message_text = "📜 Последние заказы\n\n"
        
        for idx, order in enumerate(orders):
            order_name = order.get("name", "Заказ")
            order_total = order.get("total", 0)
            order_date = order.get("createdAt", "")
            
            # Форматируем дату, если есть
            date_str = ""
            if order_date:
                try:
                    from datetime import datetime
                    if isinstance(order_date, str):
                        # Пробуем разные форматы
                        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                            try:
                                dt = datetime.strptime(order_date.split('.')[0], fmt)
                                date_str = dt.strftime("%d.%m.%Y %H:%M")
                                break
                            except:
                                continue
                except:
                    date_str = str(order_date)[:10] if len(str(order_date)) > 10 else str(order_date)
            
            message_text += f"{idx + 1}. {order_name}\n"
            if order_total:
                message_text += f"💰 {order_total} ₽\n"
            if date_str:
                message_text += f"📅 {date_str}\n"
            message_text += "\n"
        
        # Создаём клавиатуру с кнопками "Повторить" для каждого заказа
        keyboard = []
        for idx, order in enumerate(orders):
            order_keyboard = get_order_keyboard(order, idx, total_orders, user_id)
            # Добавляем кнопки из клавиатуры заказа
            if order_keyboard and order_keyboard.inline_keyboard:
                for row in order_keyboard.inline_keyboard:
                    keyboard.append(row)
        
        # Кнопка "В главное меню"
        keyboard.append([
            InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
        ])
        
        final_keyboard = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение
        if update.message:
            await update.message.reply_text(
                message_text,
                reply_markup=final_keyboard,
            )
        elif update.callback_query:
            await update.callback_query.message.edit_text(
                message_text,
                reply_markup=final_keyboard,
            )
            await update.callback_query.answer()
        
        logger.info(f"Показаны последние {total_orders} заказов для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при показе истории заказов: {e}", exc_info=True)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
        ]])
        if update.message:
            await update.message.reply_text(
                "Произошла ошибка при загрузке истории заказов.",
                reply_markup=keyboard,
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка при загрузке истории заказов.",
                reply_markup=keyboard,
            )


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает профиль пользователя"""
    try:
        user = update.effective_user
        user_id = user.id
        user_data = get_user_data(user_id)
        
        # Формируем сообщение
        message_text = format_profile_message(user, user_data)
        
        # Создаём клавиатуру
        keyboard = get_profile_keyboard(user_id)
        
        # Отправляем сообщение
        if update.message:
            await update.message.reply_text(
                message_text,
                reply_markup=keyboard,
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                message_text,
                reply_markup=keyboard,
            )
            await update.callback_query.answer()
        
        logger.info(f"Показан профиль пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при показе профиля: {e}", exc_info=True)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
        ]])
        if update.message:
            await update.message.reply_text(
                "Произошла ошибка при загрузке профиля.",
                reply_markup=keyboard,
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка при загрузке профиля.",
                reply_markup=keyboard,
            )


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает экран техподдержки"""
    try:
        logger.info(f"Показан экран техподдержки для пользователя {update.effective_user.id}")
        
        # Активируем режим техподдержки
        context.user_data["in_support_mode"] = True
        
        # Первое сообщение
        first_message = (
            "Что имеет этот бот?\n\n"
            "Привет! На связи команда поддержки!\n\n"
            "Мы поможем разобраться с любой ситуацией и будем рады просто пообщаться."
        )
        
        # Второе сообщение
        second_message = (
            "Здравствуйте! Мы ответим в течение 10 минут, но постараемся быстрее."
        )
        
        # Создаём клавиатуру
        keyboard = get_support_keyboard()
        
        # Отправляем первое сообщение
        if update.message:
            await update.message.reply_text(
                first_message,
                reply_markup=keyboard,
            )
            # Отправляем второе сообщение
            await update.message.reply_text(
                second_message,
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                first_message,
                reply_markup=keyboard,
            )
            # Отправляем второе сообщение
            await update.callback_query.message.reply_text(
                second_message,
            )
            await update.callback_query.answer()
        
        logger.info(f"Экран техподдержки показан пользователю {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при показе техподдержки: {e}", exc_info=True)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
        ]])
        if update.message:
            await update.message.reply_text(
                "Произошла ошибка при загрузке техподдержки.",
                reply_markup=keyboard,
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка при загрузке техподдержки.",
                reply_markup=keyboard,
            )


async def handle_support_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает сообщения в режиме техподдержки"""
    try:
        if not update.message or not update.message.text:
            return
        
        user_id = update.effective_user.id
        user = update.effective_user
        message_text = update.message.text
        
        logger.info(f"Получено сообщение от пользователя {user_id} в режиме техподдержки: {message_text}")
        
        # Пересылаем сообщение боту техподдержки
        if SUPPORT_BOT_TOKEN:
            try:
                # Создаём временное приложение для бота техподдержки
                from telegram import Bot
                support_bot = Bot(token=SUPPORT_BOT_TOKEN)
                
                # Формируем сообщение для техподдержки
                user_info = f"Пользователь: {user.first_name or 'Не указано'}"
                if user.username:
                    user_info += f" (@{user.username})"
                user_info += f"\nID: {user_id}"
                
                support_message = f"{user_info}\n\nСообщение:\n{message_text}"
                
                # Отправляем сообщение боту техподдержки
                # Используем user_id как chat_id (бот техподдержки должен быть запущен отдельно)
                # Или можно использовать специальный чат для техподдержки
                if SUPPORT_CHAT_ID:
                    chat_id = SUPPORT_CHAT_ID
                else:
                    # Если SUPPORT_CHAT_ID не установлен, используем user_id
                    # В этом случае бот техподдержки должен быть запущен отдельно и обрабатывать сообщения
                    chat_id = user_id
                
                try:
                    await support_bot.send_message(
                        chat_id=chat_id,
                        text=support_message
                    )
                    logger.info(f"Сообщение переслано боту техподдержки в чат {chat_id}")
                    
                    # Сохраняем связь пользователя с чатом техподдержки
                    user_support_chat_mapping[user_id] = chat_id
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения боту техподдержки: {e}")
                    # Если не удалось отправить, продолжаем работу
            except Exception as e:
                logger.error(f"Ошибка при создании бота техподдержки: {e}")
        
        # Подтверждаем получение сообщения
        keyboard = get_support_keyboard()
        await update.message.reply_text(
            "✅ Ваше сообщение получено! Мы ответим в ближайшее время.",
            reply_markup=keyboard,
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения техподдержки: {e}", exc_info=True)


async def show_documents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает раздел документов"""
    try:
        logger.info(f"Вызвана функция show_documents для пользователя {update.effective_user.id}")
        
        # Описание раздела
        description_text = (
            "📄 Документы\n\n"
            "Здесь вы найдёте все необходимые документы:\n"
            "• Юридические документы\n"
            "• Правила акций\n"
            "• Информация о составе и калорийности\n"
            "• Программа благодарности"
        )
        
        # Создаём клавиатуру
        keyboard = get_documents_keyboard()
        logger.info(f"Клавиатура документов создана: {len(keyboard.inline_keyboard)} кнопок")
        
        # Отправляем картинку, если указан URL
        if update.message:
            if DOCUMENTS_IMAGE_URL:
                try:
                    logger.info(f"Попытка отправить картинку: {DOCUMENTS_IMAGE_URL}")
                    await update.message.reply_photo(
                        photo=DOCUMENTS_IMAGE_URL,
                        caption=description_text,
                        reply_markup=keyboard,
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить картинку документов: {e}")
                    await update.message.reply_text(
                        description_text,
                        reply_markup=keyboard,
                    )
            else:
                logger.info("Отправка текстового сообщения с документами")
                await update.message.reply_text(
                    description_text,
                    reply_markup=keyboard,
                )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                description_text,
                reply_markup=keyboard,
            )
            await update.callback_query.answer()
        
        logger.info(f"Показан раздел документов для пользователя {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при показе документов: {e}", exc_info=True)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="<< Главное меню", callback_data="back_to_menu")
        ]])
        if update.message:
            await update.message.reply_text(
                "Произошла ошибка при загрузке документов.",
                reply_markup=keyboard,
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                "Произошла ошибка при загрузке документов.",
                reply_markup=keyboard,
            )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback-запросов (нажатия на inline кнопки)"""
    try:
        # Автоматическая регистрация пользователя
        await ensure_user_registered(update)
        
        query = update.callback_query
        if not query:
            return
        
        data = query.data
        user_id = update.effective_user.id
        
        if data == "back_to_menu":
            # Возврат в главное меню
            await query.answer()
            
            # Выходим из режима техподдержки, если был активен
            if context.user_data.get("in_support_mode"):
                context.user_data["in_support_mode"] = False
                logger.info(f"Пользователь {user_id} вышел из режима техподдержки")
            
            # Получаем контекст для персонализированного приветствия
            welcome_ctx = get_user_welcome_context(user_id)
            
            # Формируем персонализированное приветствие
            if welcome_ctx and welcome_ctx.get("user_name"):
                user_name = welcome_ctx.get("user_name")
                location_name = welcome_ctx.get("location_name")
                
                if location_name:
                    welcome_text = (
                        f"Привет, {user_name}! 👋\n\n"
                        f"📍 Твоя кофейня: {location_name}\n\n"
                        "Выбери действие:\n\n"
                        "📦 Открыть каталог — сразу в твою кофейню\n"
                        "📜 Мои заказы — твои предыдущие заказы\n"
                        "👤 Профиль — личные данные\n"
                        "📄 Документы — чеки и документы\n"
                        "💬 Тех поддержка — связь с поддержкой"
                    )
                else:
                    welcome_text = (
                        f"Привет, {user_name}! 👋\n\n"
                        "Выбери действие:\n\n"
                        "📦 Открыть меню — просмотр товаров\n"
                        "📜 Мои заказы — твои предыдущие заказы\n"
                        "👤 Профиль — личные данные\n"
                        "📄 Документы — чеки и документы\n"
                        "💬 Тех поддержка — связь с поддержкой"
                    )
            else:
                welcome_text = (
                    "Привет! Выбери действие:\n\n"
                    "📦 Открыть меню — просмотр товаров\n"
                    "📜 Мои заказы — твои предыдущие заказы\n"
                    "👤 Профиль — личные данные\n"
                    "📄 Документы — чеки и документы\n"
                    "💬 Тех поддержка — связь с поддержкой"
                )
            
            # Всегда отправляем новое сообщение, чтобы сохранить цепочку
            await query.message.reply_text(
                welcome_text,
                reply_markup=get_main_keyboard(user_id),
            )
            
            logger.info(f"Пользователь {user_id} вернулся в главное меню")
        
        # Обработчики главного меню
        elif data == "menu_order_history":
            await query.answer()
            await show_order_history(update, context, order_index=0)
            logger.info(f"Пользователь {user_id} открыл историю заказов")
        
        elif data == "menu_profile":
            await query.answer()
            await show_profile(update, context)
            logger.info(f"Пользователь {user_id} открыл профиль")
        
        elif data == "menu_documents":
            await query.answer()
            await show_documents(update, context)
            logger.info(f"Пользователь {user_id} открыл документы")
        
        elif data == "menu_support":
            await query.answer()
            await show_support(update, context)
            logger.info(f"Пользователь {user_id} открыл техподдержку")
        
        elif data == "noop":
            # Пустой callback (для неактивных кнопок)
            await query.answer()
        
        elif data.startswith("order_prev_"):
            # Переход к предыдущему заказу
            order_index = int(data.split("_")[-1])
            new_index = order_index - 1
            await show_order_history(update, context, order_index=new_index)
            logger.info(f"Пользователь {user_id} перешёл к заказу {new_index + 1}")
        
        elif data.startswith("order_next_"):
            # Переход к следующему заказу
            order_index = int(data.split("_")[-1])
            new_index = order_index + 1
            await show_order_history(update, context, order_index=new_index)
            logger.info(f"Пользователь {user_id} перешёл к заказу {new_index + 1}")
        
        # Обработчики профиля
        elif data == "promo_1_rub":
            # Промо "Любой напиток за 1₽"
            await query.answer("Акция для новых пользователей! При первом заказе любой напиток стоит всего 1₽", show_alert=True)
            logger.info(f"Пользователь {user_id} просмотрел промо '1 рубль'")
        
        elif data == "referral_invite":
            # Реферальная программа
            user_data = get_user_data(user_id)
            bot_username = (await context.bot.get_me()).username
            referral_link = f"https://t.me/{bot_username}?start={user_data['referral_code']}"
            
            await query.answer()
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Назад", callback_data="menu_profile")
            ]])
            await query.message.reply_text(
                f"🎁 Пригласи друга и получи бонусы!\n\n"
                f"Твоя реферальная ссылка:\n"
                f"`{referral_link}`\n\n"
                f"Когда друг зарегистрируется по твоей ссылке:\n"
                f"• Другу: +100 баллов\n"
                f"• Тебе: +200 баллов",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            logger.info(f"Пользователь {user_id} запросил реферальную ссылку")
        
        elif data == "feedback_survey":
            # Опрос/фидбек
            await query.answer()
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Назад", callback_data="menu_profile")
            ]])
            await query.message.reply_text(
                "💬 Ты любишь, мы улучшаем!\n\n"
                "Поделись своим мнением о нас и получи +200 баллов.\n\n"
                "Как вам наш кофе? (1-5 звёзд)\n"
                "Что бы вы хотели улучшить?\n\n"
                "Отправьте ваш отзыв текстом, и мы начислим вам баллы!",
                reply_markup=keyboard
            )
            # Сохраняем состояние ожидания фидбека
            context.user_data["waiting_feedback"] = True
            logger.info(f"Пользователь {user_id} начал опрос")
        
        elif data == "promo_rules":
            # Правила акции
            await query.answer()
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Назад", callback_data="menu_profile")
            ]])
            await query.message.reply_text(
                "📋 Правила акции\n\n"
                "1. Акция 'Любой напиток за 1₽' действует только для новых пользователей\n"
                "2. Акция действует при первом заказе\n"
                "3. Один пользователь может использовать акцию только один раз\n"
                "4. Акция не суммируется с другими предложениями\n"
                "5. Подробности уточняйте у администратора",
                reply_markup=keyboard
            )
            logger.info(f"Пользователь {user_id} просмотрел правила акции")
        
        elif data == "download_receipt":
            # Скачать квитанцию для юриков
            await query.answer("Генерирую квитанцию...", show_alert=False)
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Назад", callback_data="menu_profile")
            ]])
            
            # В реальном приложении здесь будет генерация PDF
            # Пока отправляем текстовое сообщение
            await query.message.reply_text(
                "📄 Квитанция для юридических лиц\n\n"
                "В разработке. Скоро здесь будет возможность скачать PDF-квитанцию с ИНН, КПП и данными о заказе.",
                reply_markup=keyboard
            )
            logger.info(f"Пользователь {user_id} запросил квитанцию")
        
        elif data == "doc_gratitude_program":
            # Программа благодарности (PDF из Google Drive)
            await query.answer("Загружаю документ...", show_alert=False)
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(text="<< Назад", callback_data="menu_documents")
            ]])
            
            try:
                # Отправляем PDF документ
                # Если это Google Drive ссылка, нужно использовать прямую ссылку для скачивания
                # Формат: https://drive.google.com/uc?export=download&id=FILE_ID
                # Или можно отправить как URL кнопку
                
                # Вариант 1: Отправка документа по URL
                await query.message.reply_document(
                    document=GRATITUDE_PROGRAM_URL,
                    caption="📄 Программа благодарности\n\nРецепты и программа лояльности",
                    reply_markup=keyboard
                )
            except Exception as e:
                # Если не удалось отправить документ, отправляем ссылку
                logger.warning(f"Не удалось отправить документ напрямую: {e}")
                await query.message.reply_text(
                    f"📄 Программа благодарности\n\n"
                    f"Скачайте документ по ссылке:\n"
                    f"{GRATITUDE_PROGRAM_URL}",
                    reply_markup=keyboard
                )
            
            logger.info(f"Пользователь {user_id} запросил программу благодарности")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике callback: {e}", exc_info=True)
        if update.callback_query:
            try:
                await update.callback_query.answer("Произошла ошибка", show_alert=True)
            except:
                pass


async def post_init(application: Application) -> None:
    """Настройка бота после инициализации (установка Menu Button)"""
    try:
        web_app_info = WebAppInfo(url=WEB_APP_URL)
        menu_button = MenuButtonWebApp(text="Перейти в меню", web_app=web_app_info)
        # Устанавливаем Menu Button глобально (chat_id=None означает глобальная установка)
        await application.bot.set_chat_menu_button(chat_id=None, menu_button=menu_button)
        logger.info("Menu Button 'Перейти в меню' установлен глобально")
    except Exception as e:
        logger.error(f"Ошибка при установке Menu Button: {e}", exc_info=True)


def main() -> None:
    """
    Точка входа: создаём приложение Telegram-бота и запускаем polling.
    """
    global application_instance
    try:
        application_instance = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

        # Регистрируем обработчик команды /start
        application_instance.add_handler(CommandHandler("start", start))
        
        # Регистрируем обработчик данных из WebApp (должен быть перед другими MessageHandler)
        application_instance.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
        
        # Регистрируем обработчик геолокации (должен быть перед TEXT)
        application_instance.add_handler(MessageHandler(filters.LOCATION, handle_message))
        
        # Регистрируем обработчик текстовых сообщений (нажатия на кнопки)
        application_instance.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Регистрируем обработчик callback-запросов (inline кнопки)
        application_instance.add_handler(CallbackQueryHandler(handle_callback_query))

        # Запуск бота
        logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
        print("Бот запущен. Нажмите Ctrl+C для остановки.")
        application_instance.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
        print("Бот остановлен.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
        print(f"Произошла ошибка: {e}")
        sys.exit(1)


