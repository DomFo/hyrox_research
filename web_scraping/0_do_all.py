import json
import pprint  # For clean dictionary printing
import re
from typing import List, Dict, Optional, Any

import requests
from bs4 import BeautifulSoup, Tag


# --- 1. GET ALL SEASONS ---

def get_all_seasons() -> List[Dict[str, Any]]:
    """Fetches the list of all available HYROX seasons."""
    url = "https://results.hyrox.com"  # Use a known season page to get the dropdown
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }

    print("\n\n1. 🔎 Fetching all available seasons...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching seasons URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    seasons = []

    # Locate the dropdown menu for seasons
    # Looking for a dropdown menu containing links like /season-X/
    season_menu = soup.find('ul', class_='dropdown-menu')

    if season_menu:
        for anchor in season_menu.find_all('a', href=True):
            relative_url = anchor.get('href')
            season_name = anchor.get_text(strip=True)

            # Use regex to reliably extract the season number from the URL part
            match = re.search(r'season-(\d+)', relative_url)
            season_num = int(match.group(1)) if match else None

            if season_num:
                seasons.append({
                    'name': season_name,
                    'number': season_num,
                    'url': f"https://results.hyrox.com{relative_url}"
                })

    # Sort and return, ensuring the latest season is last
    seasons.sort(key=lambda s: s['number'])

    if not seasons:
        # Fallback if dropdown structure changes, assuming Season 8 is current.
        print("⚠️ Could not scrape seasons; falling back to hardcoded Season 8.")
        seasons.append({'name': 'Season 8 (Fallback)', 'number': 8, 'url': 'https://results.hyrox.com/season-8/'})

    print(f"✅ Found {len(seasons)} season(s).")
    for season in seasons:
        print(f"   - {season['name']} (Number: {season['number']})")

    return seasons


# --- 2. GET EVENT MAIN GROUPS (TOWN-EVENTS) ---

def get_event_main_groups(season_number: int) -> Optional[List[Dict[str, str]]]:
    """Fetches the list of all 'Event Main Groups' (Town-Events) for a specified season."""

    BASE_URL = f"https://results.hyrox.com/season-{season_number}/index.php"
    params = {
        'content': 'ajax2',
        'func': 'getSearchFields',
        'options[lang]': 'EN_CAP',
        'options[pid]': 'start'
    }

    print(f"\n3. 🏙️ Fetching Event Main Groups for Season {season_number}...")

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        response_json = response.json()

        event_main_groups_data = (
            response_json.get('branches', {}).get('lists', {}).get('fields', {})
            .get('event_main_group', {}).get('data', [])
        )

        extracted_events = []
        for event_data in event_main_groups_data:
            if event_data.get('v') and len(event_data['v']) >= 2:
                extracted_events.append({
                    'id': event_data['v'][0],
                    'name': event_data['v'][1]
                })

        return extracted_events

    except requests.exceptions.RequestException as err:
        print(f"❌ Failed to fetch Event Main Groups: {err}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Failed to decode JSON for Event Main Groups.")
        return None


# --- 3. GET DIVISIONS (EVENTS) FOR A TOWN-EVENT ---

def get_event_divisions(season_number: int, event_main_group_id: str) -> Optional[List[Dict[str, str]]]:
    """Fetches the list of 'Events' (Divisions) for a specific Town-Event."""

    BASE_URL = f"https://results.hyrox.com/season-{season_number}/index.php"

    params = {
        'content': 'ajax2',
        'func': 'getSearchFields',
        'options[b][lists][event_main_group]': event_main_group_id,
        'options[lang]': 'EN_CAP',
        'options[pid]': 'start'
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        response_json = response.json()

        division_data = (
            response_json.get('branches', {})
            .get('lists', {})
            .get('fields', {})
            .get('event', {})
            .get('data', [])
        )

        extracted_divisions = []
        for division in division_data:
            if division.get('v') and len(division['v']) >= 2:
                extracted_divisions.append({
                    'id': division['v'][0],
                    'name': division['v'][1]
                })

        return extracted_divisions

    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None


# --- 4. REQUEST DIVISION RESULTS PAGE ---

def get_division_results_page(
        season_number: int,
        event_main_group_id: str,
        event_id: str,
        page_number: int = 1,
        sex_filter: str = '%',
        num_results: int = 25
) -> Optional[str]:
    """Sends a POST request to fetch a specific page of results."""

    BASE_URL = f"https://results.hyrox.com/season-{season_number}/"
    TARGET_PATH = "?pid=list&pidp=ranking_nav"
    URL = BASE_URL + TARGET_PATH

    payload = {
        'lang': 'EN_CAP',
        'startpage': 'start_responsive',
        'startpage_type': 'lists',
        'event_main_group': event_main_group_id,
        'event': event_id,
        'ranking': 'time_finish_netto',
        'search[name]': '',
        'search[firstname]': '',
        'search[sex]': sex_filter,
        'search[age_class]': '%',
        'search[nation]': '%',
        'num_results': str(num_results),
        'page': str(page_number),
        'submit': 'submit'
    }

    try:
        response = requests.post(URL, data=payload, timeout=30)
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as err:
        print(f"❌ Failed to fetch results page: {err}")
        return None


# --- 5. EXTRACT ROW DATA --- (Your final robust function)

def get_row_information_final(row_soup: Tag) -> Dict[str, Any]:
    """
    Extracts all athlete details from a single list item (<li> element).
    """

    data = {
        'rank': 'N/A',
        'ag_rank': 'N/A',
        'last_name': 'N/A',
        'first_name': 'N/A',
        'nationality': 'N/A',
        'age_group': 'N/A',
        'total_time': 'N/A',
        'detail_link': 'N/A'
    }

    # Rank and Age Group Rank (Uses list for robust matching)
    rank_tag = row_soup.find('div', class_=['list-field', 'type-place', 'place-primary'])
    if rank_tag:
        data['rank'] = rank_tag.text.strip()

    ag_rank_tag = row_soup.find('div', class_=['list-field', 'type-place', 'place-secondary'])
    if ag_rank_tag:
        data['ag_rank'] = ag_rank_tag.text.strip()

    # Name and Link Extraction
    h4 = row_soup.find('h4', class_='list-field type-fullname')
    a_tag = h4.find('a') if h4 else None

    if a_tag:
        data['detail_link'] = a_tag.get('href', 'N/A')
        full_name_text = a_tag.text.strip()
        if ',' in full_name_text:
            parts = full_name_text.split(',', 1)
            data['last_name'] = parts[0].strip()
            data['first_name'] = parts[-1].strip()
        else:
            data['first_name'] = full_name_text

    # Nationality (Abbreviation)
    nation_abbr_tag = row_soup.find('span', class_='nation__abbr')
    if nation_abbr_tag:
        data['nationality'] = nation_abbr_tag.text.strip()

    # Age Group
    age_group_tag = row_soup.find('div', class_=['list-field', 'type-age_class'])
    if age_group_tag:
        age_group_text = age_group_tag.get_text(strip=True)
        data['age_group'] = age_group_text.replace('AgeGroup', '').replace('Age Group', '').strip()

    # Total Time
    time_div = row_soup.find('div', class_=['right', 'list-field', 'type-time'])
    if time_div:
        time_value_div = time_div.find_all('div')[-1] if time_div.find_all('div') else time_div
        data['total_time'] = time_value_div.text.strip()

    return data


# --- 6. PARSE PAGE AND EXTRACT FIRST ROW ---

def extract_first_row(html_content: str) -> Optional[Dict[str, Any]]:
    """Parses the HTML content, finds the first athlete row, and extracts its data."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main list container
    results_list_container = soup.find('ul', class_='list-group-multicolumn')

    if not results_list_container:
        return None

    # Find all list items and filter out the header row
    rows = results_list_container.find_all('li', class_='list-group-item')
    athlete_rows = [row for row in rows if 'list-group-header' not in row.get('class', [])]

    if athlete_rows:
        # Extract the data for the very first athlete row
        return get_row_information_final(athlete_rows[0])

    return None


# =========================================================================
# --- Main Orchestration ---
# =========================================================================

# 1. Get all seasons and find the last one
seasons = get_all_seasons()

if not seasons:
    print("\nScript terminated: Could not proceed without season data.")
    exit()

# 2. Go to the last season
latest_season = seasons[-1]
SEASON_NUMBER = latest_season['number']
print(f"\n2. ➡️ Focusing on the **Latest Season**: {latest_season['name']} (Number: {SEASON_NUMBER})")
print("-" * 50)

# 3. Get all event main groups
main_groups = get_event_main_groups(SEASON_NUMBER)
print(f"\nFound {len(main_groups) if main_groups else 0} Event Main Groups for Season {SEASON_NUMBER}:")
for group in main_groups:
    print(f"   - {group['name']} (ID: {group['id']})")

if not main_groups:
    print("\nScript terminated: Could not proceed without event main groups.")
    exit()

# 4. Go to the First event main group
FIRST_MAIN_GROUP = main_groups[0]
MAIN_GROUP_ID = FIRST_MAIN_GROUP['id']
MAIN_GROUP_NAME = FIRST_MAIN_GROUP['name']
print(f"\n4. ➡️ Focusing on the **First Event Main Group**: {MAIN_GROUP_NAME} (ID: {MAIN_GROUP_ID})")
print("-" * 50)

# 5. Get all divisions (events) for this event main group
divisions = get_event_divisions(SEASON_NUMBER, MAIN_GROUP_ID)

if not divisions:
    print(f"\nScript terminated: No divisions found for {MAIN_GROUP_NAME}.")
    exit()

print(f"\n5. 🗂️ Found {len(divisions)} divisions for {MAIN_GROUP_NAME}:")
for division in divisions:
    print(f"   - {division['name']} (ID: {division['id']})")
print("-" * 50)

# 6. Request data for the first event
FIRST_DIVISION = divisions[0]
DIVISION_ID = FIRST_DIVISION['id']
DIVISION_NAME = FIRST_DIVISION['name']
print(f"\n6. 📥 Requesting results for **First Division**: {DIVISION_NAME} (ID: {DIVISION_ID})")

html_content = get_division_results_page(
    season_number=SEASON_NUMBER,
    event_main_group_id=MAIN_GROUP_ID,
    event_id=DIVISION_ID,
    page_number=1,
    sex_filter='%',  # Use '%' to get all sexes unless specified
    num_results=25
)

# 7. Extract the data and 8. Print the first row
if html_content:
    print(f"\n7. & 8. 📄 Extracting data from results page (Page 1)...")
    first_athlete_data = extract_first_row(html_content)

    if first_athlete_data:
        print("\n**✅ FIRST ATHLETE ROW DATA EXTRACTED SUCCESSFULLY:**")
        pprint.pprint(first_athlete_data, indent=4)
    else:
        print("❌ Could not extract any athlete data from the fetched page.")
