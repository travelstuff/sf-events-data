import requests
import json
import re
from datetime import datetime

session = requests.Session()
HEADERS = {"User-Agent": "SFGuideBot/1.0"}

def fetch_sflive():
    try:
        r = requests.get("https://sflive.art/wp-json/vibemap/v1/events-data?per_page=1000", headers=HEADERS, timeout=30)
        return r.json() if r.status_code == 200 else []
    except: return []

def fetch_funcheap():
    events = []
    for page in range(1, 4):
        try:
            r = requests.get(f"https://sf.funcheap.com/wp-json/wp/v2/cityguide?per_page=100&page={page}", headers=HEADERS, timeout=30)
            if r.status_code != 200 or not r.json(): break
            events.extend(r.json())
        except: break
    return events

print("Fetching data...")
all_raw = fetch_sflive() + fetch_funcheap()
unique = {}

for raw in all_raw:
    title = raw.get('title', {}).get('rendered', 'No title') if isinstance(raw.get('title'), dict) else raw.get('title', 'No title')
    link = raw.get('link', '')
    start_date = raw.get('vibemap_event_start_date') or raw.get('date', '')[:10]
    
    photo = ''
    if raw.get('uagb_featured_image_src'):
        photo = raw['uagb_featured_image_src'].get('full', [''])[0]
    
    unique[link] = {
        "title": title,
        "link": link,
        "start_date": start_date,
        "venue": raw.get('vibemap_event_venue_name') or 'San Francisco',
        "photo": photo,
        "is_free": 'free' in str(title).lower() or 'funcheap' in link
    }

data = {"events": list(unique.values()), "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC")}
with open("events.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"Saved {len(data['events'])} events.")
