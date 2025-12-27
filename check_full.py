"""Check all data needed for auto-location selection"""
import os
import sys

# Redirect to file
sys.stdout = open('check_full_output.txt', 'w', encoding='utf-8')

os.environ['SUPABASE_URL'] = 'https://wntvxdgxzenehfzvorae.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndudHZ4ZGd4emVuZWhmenZvcmFlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMTQxMDgsImV4cCI6MjA4MDY5MDEwOH0.2CGjqmX-5wwgMmBKLrft9BxlcDG0bR4XDy0pT8hYNU0'

from supabase import create_client
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_ANON_KEY'])

print('=' * 60)
print('FULL DATA CHECK FOR AUTO-LOCATION')
print('=' * 60)

# 1. Check locations
print('\n1. LOCATIONS (status + isAcceptingOrders):')
locs = supabase.table('Location').select('id, name, status, isAcceptingOrders').execute()
arbak_id = None
for loc in locs.data:
    is_active = loc.get('status') == 'active' and loc.get('isAcceptingOrders') == True
    status = 'ACTIVE' if is_active else 'INACTIVE'
    print(f"   [{status}] {loc['name']}: status={loc.get('status')}, accepting={loc.get('isAcceptingOrders')}")
    if 'Арбак' in loc.get('name', '') or 'арбак' in loc.get('name', '').lower():
        arbak_id = loc.get('id')
        print(f"      ^ This is ARBAK, id={arbak_id}")

# 2. Check users and their preferredLocationId
print('\n2. USERS with preferredLocationId:')
users = supabase.table('User').select('id, telegramId, telegram_user_id, preferredLocationId, telegramUsername').limit(10).execute()
for user in users.data:
    tid = user.get('telegramId')
    tuid = user.get('telegram_user_id')
    plid = user.get('preferredLocationId')
    uname = user.get('telegramUsername')
    
    # Check if preferredLocationId matches Arbak
    is_arbak = plid == arbak_id if arbak_id else False
    
    print(f"   User: telegramId={tid}, telegram_user_id={tuid}")
    print(f"         preferredLocationId={plid[:8] if plid else None}... {'(ARBAK!)' if is_arbak else ''}")
    print(f"         username={uname}")

# 3. Simulate what WebApp would do
print('\n3. SIMULATING WEBAPP LOGIC:')
test_telegram_id = 219951825  # Your telegram ID
print(f'   Testing with telegram_id={test_telegram_id}')

# Try to find by telegramId (BigInt)
resp = supabase.table('User').select('preferredLocationId').eq('telegramId', test_telegram_id).limit(1).execute()
if resp.data and len(resp.data) > 0:
    print(f'   Found by telegramId: preferredLocationId={resp.data[0].get("preferredLocationId")}')
else:
    print('   NOT found by telegramId')
    # Try telegram_user_id
    resp = supabase.table('User').select('preferredLocationId').eq('telegram_user_id', str(test_telegram_id)).limit(1).execute()
    if resp.data and len(resp.data) > 0:
        print(f'   Found by telegram_user_id: preferredLocationId={resp.data[0].get("preferredLocationId")}')
    else:
        print('   NOT found by telegram_user_id either!')

# 4. Check if preferredLocationId is in active locations
print('\n4. CHECK preferredLocationId IN ACTIVE LOCATIONS:')
active_locs = supabase.table('Location').select('id, name').eq('status', 'active').eq('isAcceptingOrders', True).execute()
active_ids = [l['id'] for l in active_locs.data]
print(f'   Active location IDs: {[id[:8] + "..." for id in active_ids]}')

if arbak_id:
    if arbak_id in active_ids:
        print(f'   ARBAK is in active locations!')
    else:
        print(f'   ARBAK is NOT in active locations!')

print('\n' + '=' * 60)
print('DONE')
print('=' * 60)

sys.stdout.close()

