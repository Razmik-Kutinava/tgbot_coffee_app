#!/usr/bin/env python3
"""Тестирование исправленной функции build_catalog_url"""
import os
import sys

# Setup environment
os.environ['SUPABASE_URL'] = 'https://wntvxdgxzenehfzvorae.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0'

from supabase import create_client
import urllib.parse
import base64
import json

# Initialize Supabase
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])
WEB_APP_URL = "https://fl-mini-app-v3.onrender.com"

def get_user_location_context(user_id: int):
    """Simplified version from bot.py"""
    try:
        # Find user
        user_resp = supabase.table("User").select("*").eq("telegramId", user_id).limit(1).execute()
        if not user_resp.data:
            return None

        user_row = user_resp.data[0]
        preferred_location_id = user_row.get("preferredLocationId")

        if preferred_location_id:
            # Get location
            loc_resp = supabase.table("Location").select("id, latitude, longitude, name").eq("id", preferred_location_id).limit(1).execute()
            if loc_resp.data:
                loc = loc_resp.data[0]
                return {
                    "location_id": loc.get("id"),
                    "lat": loc.get("latitude"),
                    "lon": loc.get("longitude"),
                    "name": loc.get("name")
                }
    except Exception as e:
        print(f"Error: {e}")

    return None

def build_catalog_url_NEW(user_id: int) -> str:
    """NEW VERSION: Uses fragment (hash) only"""
    web_app_url = WEB_APP_URL

    ctx = get_user_location_context(user_id)

    if ctx and ctx.get("location_id"):
        location_data = {
            "action": "open_catalog",
            "location_id": ctx["location_id"],
            "latitude": ctx.get("lat"),
            "longitude": ctx.get("lon"),
            "location_name": ctx.get("name")
        }

        # Method 1: Simple query string in fragment
        params_str = urllib.parse.urlencode(location_data, doseq=False)

        # Method 2: Base64 JSON for complex frontends
        json_str = json.dumps(location_data, ensure_ascii=False)
        b64_data = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('ascii')

        web_app_url = f"{WEB_APP_URL}#{params_str}&data={b64_data}"

        return web_app_url, location_data, params_str, b64_data

    return web_app_url, None, None, None

def build_catalog_url_OLD(user_id: int) -> str:
    """OLD VERSION: Uses query string + hash"""
    web_app_url = WEB_APP_URL

    ctx = get_user_location_context(user_id)

    if ctx and ctx.get("location_id"):
        params = {
            "action": "open_catalog",
            "location_id": ctx["location_id"],
            "latitude": str(ctx.get("lat")),
            "longitude": str(ctx.get("lon")),
            "location_name": ctx.get("name")
        }

        query_string = urllib.parse.urlencode(params, doseq=False)
        web_app_url = f"{WEB_APP_URL}?{query_string}#{query_string}"

        return web_app_url

    return web_app_url

print("="*80)
print("TESTING CATALOG URL GENERATION - OLD vs NEW")
print("="*80)

test_user_id = 219951825

print("\n1. OLD VERSION (query + hash):")
print("-" * 80)
old_url = build_catalog_url_OLD(test_user_id)
print(f"URL: {old_url}")
print(f"Length: {len(old_url)}")

print("\n2. NEW VERSION (fragment only):")
print("-" * 80)
new_url, location_data, params_str, b64_data = build_catalog_url_NEW(test_user_id)
print(f"URL: {new_url}")
print(f"Length: {len(new_url)}")
print(f"\nLocation data: {location_data}")
print(f"\nFragment params: {params_str}")
print(f"\nBase64 JSON: {b64_data}")

# Decode base64 to verify
if b64_data:
    decoded = base64.urlsafe_b64decode(b64_data.encode('ascii')).decode('utf-8')
    print(f"\nDecoded JSON: {decoded}")
    print(f"Parsed: {json.loads(decoded)}")

print("\n3. COMPARISON:")
print("-" * 80)
print(f"OLD uses query string: {'?' in old_url}")
print(f"NEW uses query string: {'?' in new_url}")
print(f"OLD has fragment: {'#' in old_url}")
print(f"NEW has fragment: {'#' in new_url}")

print("\n4. WEBAPP INTEGRATION INSTRUCTIONS:")
print("-" * 80)
print("""
WebApp должен при загрузке проверить fragment (hash):

JavaScript пример:
```javascript
// Method 1: Parse simple params from hash
const hash = window.location.hash.substring(1); // remove #
const params = new URLSearchParams(hash);
const locationId = params.get('location_id');
const latitude = params.get('latitude');
const longitude = params.get('longitude');

// Method 2: Parse base64 JSON if needed
const dataParam = params.get('data');
if (dataParam) {
    const decoded = atob(dataParam); // base64 decode
    const locationData = JSON.parse(decoded);
    // Use locationData.location_id, locationData.latitude, etc.
}

// Navigate to location if found
if (locationId) {
    navigateToLocation(locationId, latitude, longitude);
}
```

React Router пример:
```javascript
useEffect(() => {
    const hash = window.location.hash;
    if (hash) {
        const params = new URLSearchParams(hash.substring(1));
        const locationId = params.get('location_id');
        if (locationId) {
            router.push(`/catalog/${locationId}`);
        }
    }
}, []);
```
""")

print("\n" + "="*80)
print("DONE")
print("="*80)
