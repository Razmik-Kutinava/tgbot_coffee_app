# WebApp Integration: Открытие каталога с последней локацией

## Быстрый старт

Добавьте этот код в главный файл вашего WebApp (App.tsx/App.jsx):

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function App() {
    const navigate = useNavigate();

    useEffect(() => {
        // Проверяем hash параметры при загрузке
        const checkLocationFromHash = () => {
            const hash = window.location.hash;
            if (!hash) {
                // Если hash нет, проверяем localStorage
                const savedLocationId = localStorage.getItem('lastLocationId');
                if (savedLocationId) {
                    console.log('Восстанавливаем последнюю локацию из localStorage:', savedLocationId);
                    navigate(`/catalog/${savedLocationId}`);
                }
                return;
            }

            // Парсим параметры из hash
            const params = new URLSearchParams(hash.substring(1));
            const locationId = params.get('location_id');
            const locationName = params.get('location_name');

            if (locationId) {
                console.log('Открываем каталог для локации:', locationName || locationId);

                // Сохраняем для следующих открытий
                localStorage.setItem('lastLocationId', locationId);
                if (locationName) {
                    localStorage.setItem('lastLocationName', locationName);
                }

                // Переходим к локации
                navigate(`/catalog/${locationId}`);
            }
        };

        checkLocationFromHash();
    }, [navigate]);

    return (
        <div className="App">
            {/* Ваш код */}
        </div>
    );
}

export default App;
```

## Детальное объяснение

### Формат URL от бота

Бот теперь отправляет URL вида:

```
https://fl-mini-app-v3.onrender.com#action=open_catalog&location_id=bfc54344-5584-4f33-a56d-2099e3af5588&latitude=55.7558&longitude=37.6173&location_name=Арбак&data=eyJhY3Rpb24iOi...
```

### Структура параметров в hash

1. **Простые параметры** (для быстрого доступа):
   - `action=open_catalog` - тип действия
   - `location_id=xxx` - UUID локации
   - `latitude=55.7558` - широта
   - `longitude=37.6173` - долгота
   - `location_name=Арбак` - название локации (URL encoded)

2. **Base64 JSON** (опционально, для сложных случаев):
   - `data=eyJhY3Rpb24iOi...` - все данные в JSON формате, закодированные в base64

### Вариант 1: Простая реализация

```typescript
// utils/locationParser.ts
export function parseLocationFromHash(): LocationData | null {
    const hash = window.location.hash;
    if (!hash) return null;

    const params = new URLSearchParams(hash.substring(1));
    const locationId = params.get('location_id');

    if (!locationId) return null;

    return {
        locationId,
        latitude: parseFloat(params.get('latitude') || '0'),
        longitude: parseFloat(params.get('longitude') || '0'),
        name: decodeURIComponent(params.get('location_name') || '')
    };
}

// App.tsx
useEffect(() => {
    const locationData = parseLocationFromHash();

    if (locationData) {
        // Сохраняем в localStorage
        localStorage.setItem('lastLocation', JSON.stringify(locationData));

        // Переходим к локации
        navigate(`/catalog/${locationData.locationId}`);
    } else {
        // Восстанавливаем из localStorage
        const saved = localStorage.getItem('lastLocation');
        if (saved) {
            const locationData = JSON.parse(saved);
            navigate(`/catalog/${locationData.locationId}`);
        }
    }
}, []);
```

### Вариант 2: С поддержкой Base64 JSON

```typescript
// utils/locationParser.ts
export function parseLocationFromHash(): LocationData | null {
    const hash = window.location.hash;
    if (!hash) return null;

    const params = new URLSearchParams(hash.substring(1));

    // Пробуем прочитать base64 JSON
    const dataParam = params.get('data');
    if (dataParam) {
        try {
            const decoded = atob(dataParam);
            const locationData = JSON.parse(decoded);
            return {
                locationId: locationData.location_id,
                latitude: locationData.latitude,
                longitude: locationData.longitude,
                name: locationData.location_name
            };
        } catch (error) {
            console.error('Failed to parse base64 location data:', error);
        }
    }

    // Fallback на простые параметры
    const locationId = params.get('location_id');
    if (locationId) {
        return {
            locationId,
            latitude: parseFloat(params.get('latitude') || '0'),
            longitude: parseFloat(params.get('longitude') || '0'),
            name: params.get('location_name') || ''
        };
    }

    return null;
}
```

### Вариант 3: React Context

```typescript
// contexts/LocationContext.tsx
import { createContext, useContext, useEffect, useState } from 'react';

interface LocationContextType {
    currentLocation: LocationData | null;
    setCurrentLocation: (location: LocationData) => void;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

export function LocationProvider({ children }) {
    const [currentLocation, setCurrentLocation] = useState<LocationData | null>(null);

    useEffect(() => {
        // Проверяем hash при загрузке
        const locationData = parseLocationFromHash();

        if (locationData) {
            setCurrentLocation(locationData);
            localStorage.setItem('lastLocation', JSON.stringify(locationData));
        } else {
            // Восстанавливаем из localStorage
            const saved = localStorage.getItem('lastLocation');
            if (saved) {
                setCurrentLocation(JSON.parse(saved));
            }
        }
    }, []);

    return (
        <LocationContext.Provider value={{ currentLocation, setCurrentLocation }}>
            {children}
        </LocationContext.Provider>
    );
}

export function useLocation() {
    const context = useContext(LocationContext);
    if (!context) {
        throw new Error('useLocation must be used within LocationProvider');
    }
    return context;
}

// App.tsx
function App() {
    return (
        <LocationProvider>
            <Router>
                <Routes>
                    <Route path="/catalog/:locationId" element={<Catalog />} />
                    {/* другие роуты */}
                </Routes>
            </Router>
        </LocationProvider>
    );
}

// Catalog.tsx
function Catalog() {
    const { currentLocation } = useLocation();
    const { locationId } = useParams();

    useEffect(() => {
        if (currentLocation && locationId === currentLocation.locationId) {
            console.log('Открываем локацию:', currentLocation.name);
            // Загружаем данные локации
        }
    }, [currentLocation, locationId]);

    return (
        <div>
            <h1>{currentLocation?.name}</h1>
            {/* контент каталога */}
        </div>
    );
}
```

## Тестирование

### 1. Локальное тестирование

Откройте DevTools и выполните:

```javascript
// Симулируем открытие с параметрами
window.location.hash = '#action=open_catalog&location_id=bfc54344-5584-4f33-a56d-2099e3af5588&location_name=Арбак';

// Проверяем парсинг
const hash = window.location.hash.substring(1);
const params = new URLSearchParams(hash);
console.log('Location ID:', params.get('location_id'));
console.log('Location Name:', params.get('location_name'));

// Проверяем localStorage
localStorage.setItem('lastLocationId', 'bfc54344-5584-4f33-a56d-2099e3af5588');
console.log('Saved:', localStorage.getItem('lastLocationId'));
```

### 2. Тестирование в Telegram

1. Запустите бота
2. Нажмите "Открыть каталог"
3. В WebApp откройте DevTools
4. Проверьте:
   ```javascript
   console.log('Hash:', window.location.hash);
   console.log('Params:', new URLSearchParams(window.location.hash.substring(1)));
   console.log('localStorage:', localStorage.getItem('lastLocationId'));
   ```

### 3. Проверка навигации

```javascript
// Должно произойти автоматически при загрузке
// Если не работает, проверьте:

console.log('Current route:', window.location.pathname);
console.log('Should navigate to:', `/catalog/${locationId}`);
```

## Troubleshooting

### Проблема: Hash не читается

**Решение:**
```typescript
// Убедитесь, что читаете hash ПОСЛЕ загрузки
useEffect(() => {
    // Задержка для гарантии загрузки
    setTimeout(() => {
        const hash = window.location.hash;
        console.log('Hash after delay:', hash);
    }, 100);
}, []);
```

### Проблема: Навигация не срабатывает

**Решение:**
```typescript
// Используйте replace вместо navigate для первой загрузки
if (locationId) {
    window.location.replace(`/catalog/${locationId}`);
}

// Или для React Router:
navigate(`/catalog/${locationId}`, { replace: true });
```

### Проблема: localStorage не сохраняется

**Решение:**
```typescript
// Проверьте права на localStorage в Telegram WebApp
try {
    localStorage.setItem('test', 'test');
    console.log('localStorage работает');
} catch (error) {
    console.error('localStorage заблокирован:', error);
    // Используйте Telegram.WebApp.CloudStorage как альтернативу
}
```

## Дополнительные улучшения

### 1. Preload данных локации

```typescript
useEffect(() => {
    const locationData = parseLocationFromHash();

    if (locationData) {
        // Preload данных локации
        fetch(`/api/locations/${locationData.locationId}`)
            .then(res => res.json())
            .then(data => {
                // Сохраняем полные данные
                localStorage.setItem('locationData', JSON.stringify(data));
            });
    }
}, []);
```

### 2. Анимация перехода

```typescript
if (locationData) {
    // Плавный переход с анимацией
    navigate(`/catalog/${locationData.locationId}`, {
        state: { fromDeepLink: true }
    });
}

// В Catalog.tsx
const location = useLocation();
const fromDeepLink = location.state?.fromDeepLink;

if (fromDeepLink) {
    // Показываем приветствие или анимацию
}
```

### 3. Аналитика

```typescript
if (locationData) {
    // Отправляем событие в аналитику
    analytics.track('catalog_opened_from_deeplink', {
        locationId: locationData.locationId,
        locationName: locationData.name,
        timestamp: new Date().toISOString()
    });
}
```

## Итого

1. ✅ Читайте `window.location.hash` при загрузке
2. ✅ Сохраняйте `lastLocationId` в `localStorage`
3. ✅ Автоматически переходите к локации
4. ✅ Обрабатывайте случай без hash (читайте из localStorage)

Это обеспечит плавный UX при открытии каталога с последней использованной локацией!
