#!/usr/bin/env python3
"""Простой тест URL генерации без Supabase"""
import urllib.parse
import base64
import json

WEB_APP_URL = "https://fl-mini-app-v3.onrender.com"

# Симулируем данные локации (Арбак)
location_data_mock = {
    "location_id": "bfc54344-5584-4f33-a56d-2099e3af5588",
    "lat": 55.7558,
    "lon": 37.6173,
    "name": "Арбак"
}

def build_catalog_url_OLD() -> str:
    """OLD VERSION: query + hash"""
    params = {
        "action": "open_catalog",
        "location_id": location_data_mock["location_id"],
        "latitude": str(location_data_mock["lat"]),
        "longitude": str(location_data_mock["lon"]),
        "location_name": location_data_mock["name"]
    }
    query_string = urllib.parse.urlencode(params, doseq=False)
    return f"{WEB_APP_URL}?{query_string}#{query_string}"

def build_catalog_url_NEW() -> tuple:
    """NEW VERSION: fragment only + base64"""
    location_data = {
        "action": "open_catalog",
        "location_id": location_data_mock["location_id"],
        "latitude": location_data_mock["lat"],
        "longitude": location_data_mock["lon"],
        "location_name": location_data_mock["name"]
    }

    # Simple params in fragment
    params_str = urllib.parse.urlencode(location_data, doseq=False)

    # Base64 JSON
    json_str = json.dumps(location_data, ensure_ascii=False)
    b64_data = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')

    url = f"{WEB_APP_URL}#{params_str}&data={b64_data}"

    return url, params_str, b64_data, location_data

print("="*80)
print("TELEGRAM MINI APP - CATALOG URL FIX TEST")
print("="*80)

print("\n1. СТАРАЯ ВЕРСИЯ (query + hash - НЕ РАБОТАЕТ):")
print("-"*80)
old_url = build_catalog_url_OLD()
print(old_url)
print(f"\n✗ Проблема: Telegram игнорирует query string параметры")
print(f"✗ WebApp открывается на главной странице, не на последней локации")

print("\n2. НОВАЯ ВЕРСИЯ (только fragment/hash - РАБОТАЕТ):")
print("-"*80)
new_url, params_str, b64_data, location_data = build_catalog_url_NEW()
print(new_url)
print(f"\n✓ Решение: Все параметры в fragment (hash)")
print(f"✓ WebApp читает window.location.hash при загрузке")

print("\n3. ДАННЫЕ ДЛЯ WEBAPP:")
print("-"*80)
print(f"Fragment params: {params_str}")
print(f"\nBase64 JSON: {b64_data}")
decoded = base64.urlsafe_b64decode(b64_data.encode('ascii')).decode('utf-8')
print(f"\nDecoded: {decoded}")

print("\n4. КОД ДЛЯ WEBAPP (JavaScript):")
print("-"*80)
print("""
// При загрузке WebApp:
const hash = window.location.hash.substring(1); // убираем #
const params = new URLSearchParams(hash);

// Вариант 1: Простые параметры
const locationId = params.get('location_id');
const latitude = params.get('latitude');
const longitude = params.get('longitude');
const locationName = params.get('location_name');

console.log('Location ID:', locationId);
console.log('Name:', locationName);

// Вариант 2: Base64 JSON (если нужно)
const dataParam = params.get('data');
if (dataParam) {
    const decoded = atob(dataParam);
    const locationData = JSON.parse(decoded);
    console.log('Full data:', locationData);
}

// Перенаправить на страницу локации
if (locationId) {
    // Для React Router:
    router.push(`/location/${locationId}`);

    // Или для обычного SPA:
    window.location.href = `/catalog?location=${locationId}`;
}
""")

print("\n5. ИНСТРУКЦИЯ ДЛЯ ФРОНТЕНДА:")
print("-"*80)
print("""
1. В App.tsx/App.jsx добавить проверку hash при монтировании:

   useEffect(() => {
       const checkHashParams = () => {
           const hash = window.location.hash;
           if (!hash) return;

           const params = new URLSearchParams(hash.substring(1));
           const locationId = params.get('location_id');

           if (locationId) {
               // Сохранить в localStorage для следующих открытий
               localStorage.setItem('lastLocationId', locationId);

               // Перейти к локации
               navigate(`/catalog/${locationId}`);
           }
       };

       checkHashParams();
   }, []);

2. При следующем открытии читать из localStorage:

   useEffect(() => {
       const lastLocationId = localStorage.getItem('lastLocationId');
       if (lastLocationId && !window.location.hash) {
           navigate(`/catalog/${lastLocationId}`);
       }
   }, []);
""")

print("\n" + "="*80)
print("ТЕСТ ЗАВЕРШЁН")
print("="*80)
