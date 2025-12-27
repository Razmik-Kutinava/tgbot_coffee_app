#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Supabase connection and user search"""

import os
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wntvxdgxzenehfzvorae.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0")

print("=" * 50)
print("Test Supabase connection")
print("=" * 50)
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_KEY[:20]}...")

try:
    from supabase import create_client
    print("\n[OK] Supabase library imported")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Supabase client created")
    
    # Test 1: Get users
    print("\n" + "=" * 50)
    print("Test 1: Get users from User table")
    print("=" * 50)
    
    users = supabase.table("User").select("id, telegramId, telegram_user_id, telegramUsername, telegramFirstName, preferredLocationId").limit(10).execute()
    
    if users.data:
        print(f"[OK] Found {len(users.data)} users:")
        for u in users.data:
            print(f"  - id: {u.get('id')[:8] if u.get('id') else 'None'}...")
            print(f"    telegramId: {u.get('telegramId')}")
            print(f"    telegram_user_id: {u.get('telegram_user_id')}")
            print(f"    username: {u.get('telegramUsername')}")
            print(f"    firstName: {u.get('telegramFirstName')}")
            print(f"    preferredLocationId: {u.get('preferredLocationId')}")
            print()
    else:
        print("[WARN] No users found")
    
    # Test 2: Get locations
    print("\n" + "=" * 50)
    print("Test 2: Get locations from Location table")
    print("=" * 50)
    
    locations = supabase.table("Location").select("id, name, latitude, longitude").limit(5).execute()
    
    if locations.data:
        print(f"[OK] Found {len(locations.data)} locations:")
        for loc in locations.data:
            print(f"  - {loc.get('name')}: lat={loc.get('latitude')}, lon={loc.get('longitude')}, id={loc.get('id')[:8]}...")
    else:
        print("[WARN] No locations found")
    
    # Test 3: Get orders
    print("\n" + "=" * 50)
    print("Test 3: Get orders from Order table")
    print("=" * 50)
    
    orders = supabase.table("Order").select("id, userId, locationId, status, paymentStatus").limit(5).execute()
    
    if orders.data:
        print(f"[OK] Found {len(orders.data)} orders:")
        for o in orders.data:
            print(f"  - userId: {o.get('userId')[:8] if o.get('userId') else 'None'}...")
            print(f"    locationId: {o.get('locationId')[:8] if o.get('locationId') else 'None'}...")
            print(f"    status: {o.get('status')}, paymentStatus: {o.get('paymentStatus')}")
            print()
    else:
        print("[WARN] No orders found")
    
    print("\n" + "=" * 50)
    print("Test completed successfully")
    print("=" * 50)
    
except ImportError as e:
    print(f"\n[ERROR] Import error: {e}")
    print("Install: pip install supabase==2.3.0")
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
