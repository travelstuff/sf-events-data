import requests
import json
import re
from datetime import datetime

session = requests.Session()
HEADERS = {"User-Agent": "SFGuideBot/1.0"}

def fetch_sflive():
    try:
        r = requests.get("https://sflive.art/wp-json/vibemap/v1/events-data?per_page=1000", headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            # If data is a dict with an 'events' key, return just the list
            if isinstance(data, dict):
                return data.get('events', [])
            return data if isinstance(data, list) else []
    except:
        pass
    return []

def fetch_funcheap():
    events = []
    # Fetch first 3 pages (300 events)
    for page in range(1, 4):
        try:
            r = requests.get(f"https://sf.funcheap.com/wp-json/wp/v2/cityguide?per_page=100&page={page}", headers=HEADERS, timeout=30)
            if r.status_code != 200: break
            batch = r.json()
            if not batch or not isinstance(batch, list): break
            events.extend(batch)
        except:
            break
    return events

print("Fetching data from sources...")
sf_list = fetch_sflive()
fc_list = fetch_funcheap()

print(f"Found {len(sf_list)} from SF Live and {len(fc_list)} from Funcheap")

all_raw = sf_list + fc_list
unique = {}

for raw in all_raw:
    # Handle different title formats
    title_data = raw.get('title', 'No title')
    title = title_data.get('rendered', 'No title') if isinstance(title_data, dict) else title_data
    
    link = raw.get('link', '')
    if not link: continue

    # Get date
    start_date = raw.get('vibemap_event_start_date') or raw.get('date', '')[:10]
    
    # Handle photo
    photo = ''
    img_src = raw.get('uagb_featured_image_src')
    if isinstance(img_src, dict):
        photo = img_src.get('full', [''])[0]

    unique[link] = {
        "title": title,
        "link": link,
        "start_date": start_date,
        "venue": raw.get('vibemap_event_venue_name') or 'San Francisco',
        "photo": photo,
        "is_free": 'free' in str(title).lower() or 'sf.funcheap.com' in link
    }

# Save final data
final_data = {
    "events": list(unique.values()),
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC")
}

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {len(final_data['events'])} events to events.json")
