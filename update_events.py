import requests
import json
from datetime import datetime

session = requests.Session()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

def fetch_sflive():
    url = "https://sflive.art/wp-json/vibemap/v1/events-data"
    params = {"per_page": 500}
    try:
        print("Requesting sflive.art...")
        r = session.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                events = data.get('events') or data.get('data') or []
                return events
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"SF Live Error: {e}")
    return []

def fetch_funcheap():
    events = []
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

# 1. Fetch data
sf_list = fetch_sflive()
fc_list = fetch_funcheap()

print(f"SF Live: {len(sf_list)} | Funcheap: {len(fc_list)}")

all_raw = sf_list + fc_list
unique = {}

# 2. Process Data
for raw in all_raw:
    t_data = raw.get('title', 'No Title')
    title = t_data.get('rendered', 'No Title') if isinstance(t_data, dict) else t_data
    
    link = raw.get('link', '')
    if not link: continue

    start_date = raw.get('vibemap_event_start_date') or raw.get('date', '')[:10]
    venue = raw.get('vibemap_event_venue_name') or 'San Francisco'
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
    "events": list(unique.values()),
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC")
}

# 4. Save Files
# Save as JSON
with open("events.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

# Save as JS Bypass (THIS IS THE MISSING PIECE)
final_json_string = json.dumps(final_data, ensure_ascii=False)
with open("events.js", "w", encoding="utf-8") as f:
    f.write(f"window.sfEventData = {final_json_string};")
