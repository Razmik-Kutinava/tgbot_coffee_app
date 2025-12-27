# Исправление: Открытие каталога с последней локацией

## Проблема

При нажатии кнопки "Открыть каталог" клиент попадал на стартовую страницу вместо последней использованной локации (кофейни).

## Диагностика

### Что работало правильно:
1. ✅ Бот получает `preferredLocationId` из БД (Арбак: bfc54344-5584-4f33-a56d-2099e3af5588)
2. ✅ Функция `get_user_location_context()` возвращает корректные данные
3. ✅ Функция `build_catalog_url()` формирует URL с параметрами

### Что НЕ работало:
❌ **WebApp не читает параметры из URL при загрузке**

### Причина:
Telegram Mini Apps **игнорирует query string параметры** при открытии WebApp.

**Старый URL (НЕ РАБОТАЕТ):**
```
https://fl-mini-app-v3.onrender.com?location_id=xxx&latitude=55.7558#location_id=xxx&latitude=55.7558
```

Telegram передаёт в WebApp только:
```
https://fl-mini-app-v3.onrender.com
```

## Решение

### 1. Изменения в bot.py

Функция `build_catalog_url()` теперь передаёт параметры **только через fragment (hash)**, добавляя также base64 JSON для сложных случаев:

**Новый URL (РАБОТАЕТ):**
```
https://fl-mini-app-v3.onrender.com#action=open_catalog&location_id=bfc54344-5584-4f33-a56d-2099e3af5588&latitude=55.7558&longitude=37.6173&location_name=Арбак&data=eyJhY3Rpb24iOiJvcGVuX2NhdGFsb2ciLCAibG9jYXRpb25faWQiOiAiYmZjNTQzNDQtNTU4NC00ZjMzLWE1NmQtMjA5OWUzYWY1NTg4IiwgImxhdGl0dWRlIjogNTUuNzU1OCwgImxvbmdpdHVkZSI6IDM3LjYxNzMsICJsb2NhdGlvbl9uYW1lIjogItCQ0YDQsdCw0LoifQ==
```

### 2. Требуемые изменения в WebApp (Frontend)

WebApp должен проверять `window.location.hash` при загрузке:

#### Вариант 1: Простой (читаем параметры из fragment)

```javascript
// В App.tsx/App.jsx при монтировании
useEffect(() => {
    const hash = window.location.hash.substring(1); // убираем #
    if (!hash) return;

    const params = new URLSearchParams(hash);
    const locationId = params.get('location_id');
    const latitude = params.get('latitude');
    const longitude = params.get('longitude');
    const locationName = params.get('location_name');

    if (locationId) {
        console.log('Opening catalog at location:', locationName);

        // Сохранить для следующих открытий
        localStorage.setItem('lastLocationId', locationId);
        localStorage.setItem('lastLocationName', locationName);

        // Перейти к локации
        navigate(`/catalog/${locationId}`);
    }
}, []);
```

#### Вариант 2: Продвинутый (читаем base64 JSON)

```javascript
useEffect(() => {
    const hash = window.location.hash.substring(1);
    if (!hash) return;

    const params = new URLSearchParams(hash);

    // Пробуем прочитать base64 JSON
    const dataParam = params.get('data');
    if (dataParam) {
        try {
            const decoded = atob(dataParam);
            const locationData = JSON.parse(decoded);

            console.log('Location data:', locationData);

            if (locationData.location_id) {
                localStorage.setItem('lastLocation', JSON.stringify(locationData));
                navigate(`/catalog/${locationData.location_id}`);
            }
        } catch (error) {
            console.error('Failed to parse location data:', error);
        }
    } else {
        // Fallback на простые параметры
        const locationId = params.get('location_id');
        if (locationId) {
            navigate(`/catalog/${locationId}`);
        }
    }
}, []);
```

#### Вариант 3: Сохранение состояния (для следующих открытий)

```javascript
// При первом открытии WebApp
useEffect(() => {
    // Проверяем hash параметры
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const locationId = params.get('location_id');

    if (locationId) {
        // Сохраняем в localStorage
        localStorage.setItem('lastLocationId', locationId);
        navigate(`/catalog/${locationId}`);
    } else {
        // Если hash нет, но есть сохранённая локация
        const savedLocationId = localStorage.getItem('lastLocationId');
        if (savedLocationId) {
            navigate(`/catalog/${savedLocationId}`);
        }
    }
}, []);
```

## Тестирование

### 1. Проверка бота

Запустить бот и посмотреть логи при нажатии /start:

```bash
python bot.py
```

В логах должно быть:
```
[CATALOG URL] Сформирован URL для пользователя 219951825:
  location_id: bfc54344-5584-4f33-a56d-2099e3af5588
  latitude: 55.7558
  longitude: 37.6173
  location_name: Арбак
  URL: https://fl-mini-app-v3.onrender.com#action=...
  Fragment: action=open_catalog&location_id=...
  Base64 JSON: eyJhY3Rpb24...
```

### 2. Проверка WebApp

1. Открыть WebApp через бота
2. Проверить в консоли браузера:
   ```javascript
   console.log('Hash:', window.location.hash);
   ```
3. Должен быть hash с параметрами локации
4. WebApp должен перейти на страницу каталога с последней локацией

### 3. Проверка localStorage

```javascript
console.log('Last location:', localStorage.getItem('lastLocationId'));
```

## Важные замечания

### Для backend (bot.py):
- ✅ Изменения уже применены в `build_catalog_url()`
- ✅ Параметры передаются через fragment (hash)
- ✅ Добавлена поддержка base64 JSON для совместимости

### Для frontend (WebApp):
- ⚠️ **ТРЕБУЕТСЯ** добавить проверку `window.location.hash` при загрузке
- ⚠️ **ТРЕБУЕТСЯ** сохранение `lastLocationId` в `localStorage`
- ⚠️ **ТРЕБУЕТСЯ** автоматическая навигация к сохранённой локации

## Альтернативные решения (на будущее)

1. **Telegram Web App initData**: Можно передавать данные через `start_param` в глубоких ссылках
2. **Backend API**: При открытии WebApp делать запрос к backend API для получения последней локации
3. **Cloud Storage**: Использовать Telegram Cloud Storage API для сохранения состояния

## Структура данных

### Base64 JSON содержит:
```json
{
    "action": "open_catalog",
    "location_id": "bfc54344-5584-4f33-a56d-2099e3af5588",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "location_name": "Арбак"
}
```

### Fragment параметры:
- `action=open_catalog` - тип действия
- `location_id=xxx` - UUID локации из БД
- `latitude=55.7558` - координаты
- `longitude=37.6173` - координаты
- `location_name=Арбак` - название (URL encoded)
- `data=xxx` - base64 JSON со всеми данными

## Проверенные случаи

1. ✅ Пользователь с `preferredLocationId` в БД
2. ✅ Локация активна (`status=active`, `isAcceptingOrders=true`)
3. ✅ URL формируется корректно
4. ⚠️ WebApp читает hash параметры - **требуется реализация на фронтенде**

## Следующие шаги

1. Реализовать чтение hash параметров в WebApp
2. Добавить навигацию к локации при открытии
3. Сохранять `lastLocationId` в `localStorage`
4. Тестировать с реальными пользователями
