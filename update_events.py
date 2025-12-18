import requests
import json
import re
from datetime import datetime

session = requests.Session()
# Adding a more "human" user agent helps prevent being blocked by site security
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}

def fetch_sflive():
    # This is the direct endpoint for their map data
    url = "https://sflive.art/wp-json/vibemap/v1/events-data"
    params = {"per_page": 500}
    try:
        print("Requesting sflive.art...")
        r = session.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            # SF Live often nests events inside a 'data' or 'events' key
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

# Execution
sf_list = fetch_sflive()
fc_list = fetch_funcheap()

print(f"--- RESULTS ---")
print(f"SF Live: {len(sf_list)} events found")
print(f"Funcheap: {len(fc_list)} events found")

all_raw = sf_list + fc_list
unique = {}

for raw in all_raw:
    # Title handling (SF Live uses 'title', Funcheap uses 'title.rendered')
    t_data = raw.get('title', 'No Title')
    title = t_data.get('rendered', 'No Title') if isinstance(t_data, dict) else t_data
    
    link = raw.get('link', '')
    if not link: continue

    # Date handling
    start_date = raw.get('vibemap_event_start_date') or raw.get('date', '')[:10]
    
    # Venue
    venue = raw.get('vibemap_event_venue_name') or 'San Francisco'

    # Photo
    photo = ''
    img = raw.get('uagb_featured_image_src')
    if isinstance(img, dict):
        photo = img.get('full', [''])[0]
    elif raw.get('featured_media_url'):
        photo = raw.get('featured_media_url')

    unique[link] = {
        "title": title,
        "link": link,
        "start_date": start_date,
        "venue": venue,
        "photo": photo,
        "is_free": 'free' in str(title).lower() or 'sf.funcheap.com' in link,
        "source": "sflive" if "sflive.art" in link else "funcheap"
    }

final_data = {
    "events": list(unique.values()),
    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC")
}

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"Success! Total unique events saved: {len(final_data['events'])}")
