import requests
import json
from datetime import datetime

session = requests.Session()
# Human-like headers to prevent being blocked by site security
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

def fetch_sflive():
    # Direct API endpoint for SF Live (vibemap)
    url = "https://sflive.art/wp-json/vibemap/v1/events-data"
    params = {"per_page": 500}
    try:
        print("Requesting sflive.art...")
        r = session.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            # SF Live nests events inside 'events' or 'data' keys
            if isinstance(data, dict):
                events = data.get('events') or data.get('data') or []
                return events
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"SF Live Error: {e}")
    return []

def fetch_funcheap():
    events = []
    # Grabbing the first 3 pages of events
    for page in range(1, 4):
        url = f"https://sf.funcheap.com/wp-json/wp/v2/cityguide?per_page=100&page={page}"
        try:
            print(f"Requesting Funcheap Page {page}...")
            r = session.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                batch = r.json()
                if not batch: break
                events.extend(batch)
            else: break
        except: break
    return events

# 1. Fetch data from both sources
sf_list = fetch_sflive()
fc_list = fetch_funcheap()

print(f"--- FETCH SUMMARY ---")
print(f"SF Live Events Found: {len(sf_list)}")
print(f"Funcheap Events Found: {len(fc_list)}")

all_raw = sf_list + fc_list
unique = {}

# 2. Process and Clean Data
for raw in all_raw:
    # Get Title (Handles two different JSON structures)
    t_data = raw.get('title', 'No Title')
    title = t_data.get('rendered', 'No Title') if isinstance(t_data, dict) else t_data
    
    link = raw.get('link', '')
    if not link: continue

    # Get Date
    start_date = raw.get('vibemap_event_start_date') or raw.get('date', '')[:10]
    
    # Get Venue
    venue = raw.get('vibemap_event_venue_name') or 'San Francisco'

    # Determine source and color/free status
    is_free = 'free' in str(title).lower() or 'sf.funcheap.com' in link

    unique[link] = {
        "title": title,
        "link": link,
        "start_date": start_date,
        "venue": venue,
        "is_free": is_free
    }

# 3. Create Final Data Object
final_data = {
