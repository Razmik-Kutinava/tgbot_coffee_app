#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test URL generation for catalog button"""

import os
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wntvxdgxzenehfzvorae.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0")
WEB_APP_URL = "https://fl-mini-app-v3.onrender.com"

print("=" * 60)
print("Test URL generation for 'Open Catalog' button")
print("=" * 60)

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Supabase connected")
    
    # Test user ID (Razmik's telegram ID)
    test_user_id = 219951825
    print(f"\nTesting for user_id: {test_user_id}")
    
    # Step 1: Find user
    print("\n--- Step 1: Find user ---")
    user_resp = supabase.table("User").select("*").eq("telegramId", test_user_id).limit(1).execute()
    
    if not user_resp.data or len(user_resp.data) == 0:
        user_resp = supabase.table("User").select("*").eq("telegram_user_id", test_user_id).limit(1).execute()
    
    if user_resp.data and len(user_resp.data) > 0:
        user = user_resp.data[0]
        print(f"[OK] User found:")
        print(f"     id: {user.get('id')}")
        print(f"     telegramId: {user.get('telegramId')}")
        print(f"     telegram_user_id: {user.get('telegram_user_id')}")
        print(f"     telegramFirstName: {user.get('telegramFirstName')}")
        print(f"     preferredLocationId: {user.get('preferredLocationId')}")
        
        preferred_location_id = user.get('preferredLocationId')
        
        if preferred_location_id:
            # Step 2: Get location
            print("\n--- Step 2: Get location ---")
            loc_resp = supabase.table("Location").select("*").eq("id", preferred_location_id).limit(1).execute()
            
            if loc_resp.data and len(loc_resp.data) > 0:
                loc = loc_resp.data[0]
                print(f"[OK] Location found:")
                print(f"     id: {loc.get('id')}")
                print(f"     name: {loc.get('name')}")
                print(f"     latitude: {loc.get('latitude')}")
                print(f"     longitude: {loc.get('longitude')}")
                
                # Step 3: Build URL
                print("\n--- Step 3: Build URL ---")
                params = {
                    "action": "open_catalog",
                    "location_id": loc.get("id"),
                }
                
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                
                if lat and lon:
                    params["latitude"] = str(lat)
                    params["longitude"] = str(lon)
                
                query_string = urllib.parse.urlencode(params)
                final_url = f"{WEB_APP_URL}?{query_string}"
                
                print(f"[OK] Generated URL:")
                print(f"     {final_url}")
                
                print("\n--- URL Parameters ---")
                for key, value in params.items():
                    print(f"     {key}: {value}")
                
            else:
                print(f"[ERROR] Location not found: {preferred_location_id}")
        else:
            print("[WARN] User has no preferredLocationId")
    else:
        print(f"[ERROR] User not found: {test_user_id}")
    
    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

