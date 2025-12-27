"""Test URL building for catalog"""
import os
import sys

# Redirect output to file
sys.stdout = open('test_url_output.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

os.environ['SUPABASE_URL'] = 'https://wntvxdgxzenehfzvorae.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0'

from supabase import create_client
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])

WEB_APP_URL = "https://fl-mini-app-v3.onrender.com"

def get_user_location_context(user_id):
    """Determines user's last location for catalog opening"""
    user_uuid = None
    preferred_location_id = None
    
    # Search by telegramId
    user_resp = supabase.table("User").select("*").eq("telegramId", user_id).limit(1).execute()
    print(f"Search by telegramId={user_id}: found {len(user_resp.data)} users")
    
    # Fallback to telegram_user_id  
    if not user_resp.data:
        user_resp = supabase.table("User").select("*").eq("telegram_user_id", user_id).limit(1).execute()
        print(f"Search by telegram_user_id={user_id}: found {len(user_resp.data)} users")
    
    if user_resp.data:
        user_row = user_resp.data[0]
        user_uuid = user_row.get("id")
        preferred_location_id = user_row.get("preferredLocationId")
        print(f"Found user: UUID={user_uuid[:8]}..., preferredLocationId={preferred_location_id[:8] if preferred_location_id else None}...")
    else:
        print(f"User not found!")
        return None
    
    if preferred_location_id:
        loc_resp = supabase.table("Location").select("*").eq("id", preferred_location_id).limit(1).execute()
        if loc_resp.data:
            loc = loc_resp.data[0]
            name = loc.get("name", "Unknown")
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            print(f"Location found: {name}, lat={lat}, lon={lon}")
            return {
                "location_id": loc.get("id"),
                "lat": lat,
                "lon": lon,
                "name": name
            }
    return None

def build_catalog_url(user_id):
    """Builds WebApp URL with location parameters"""
    import urllib.parse
    
    web_app_url = WEB_APP_URL
    params = {"action": "open_catalog"}
    
    ctx = get_user_location_context(user_id)
    
    if ctx:
        if ctx.get("location_id"):
            params["location_id"] = ctx["location_id"]
        if ctx.get("lat") and ctx.get("lon"):
            params["latitude"] = str(ctx["lat"])
            params["longitude"] = str(ctx["lon"])
        if ctx.get("name"):
            params["location_name"] = ctx["name"]
    
    if len(params) > 1:
        query_string = urllib.parse.urlencode(params, doseq=False)
        web_app_url = f"{WEB_APP_URL}?{query_string}#{query_string}"
    
    return web_app_url

# Test with known user IDs
print("=" * 60)
print("Testing URL building for catalog")
print("=" * 60)

test_ids = [219951825, 1846793875, 885203094, 183760838]
for tid in test_ids:
    print(f"\n=== Testing user_id={tid} ===")
    url = build_catalog_url(tid)
    print(f"Generated URL:\n{url}")
    print("-" * 60)

# Close the output file
sys.stdout.close()

