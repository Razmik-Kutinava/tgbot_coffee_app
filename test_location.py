"""Test script for location functions"""
import os
import sys

os.environ['SUPABASE_URL'] = 'https://wntvxdgxzenehfzvorae.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0'

print("=== Test Supabase Connection ===")

try:
    from supabase import create_client
    print("[OK] supabase imported")
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)

try:
    supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])
    print("[OK] Connected to Supabase")
except Exception as e:
    print(f"[ERROR] Connection error: {e}")
    sys.exit(1)

print("\n=== Check User table ===")
try:
    result = supabase.table("User").select("id, telegramId, telegram_user_id, preferredLocationId, telegramUsername").limit(5).execute()
    print(f"[OK] Found {len(result.data)} users:")
    for user in result.data:
        tid = user.get('telegramId')
        tuid = user.get('telegram_user_id')
        plid = user.get('preferredLocationId')
        print(f"   - telegramId: {tid}, telegram_user_id: {tuid}, preferredLocationId: {plid}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n=== Check Order table ===")
try:
    result = supabase.table("Order").select("id, userId, locationId, status, paymentStatus").order("createdAt", desc=True).limit(5).execute()
    print(f"[OK] Found {len(result.data)} orders:")
    for order in result.data:
        uid = order.get('userId')
        lid = order.get('locationId')
        print(f"   - userId: {uid[:8] if uid else 'None'}..., locationId: {lid[:8] if lid else 'None'}..., status: {order.get('status')}, paymentStatus: {order.get('paymentStatus')}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n=== Check Location table ===")
try:
    result = supabase.table("Location").select("id, name, latitude, longitude").limit(5).execute()
    print(f"[OK] Found {len(result.data)} locations:")
    for loc in result.data:
        print(f"   - name: {loc.get('name')}, lat: {loc.get('latitude')}, lon: {loc.get('longitude')}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n=== Done ===")

