import json
import re
import time
from datetime import datetime as dt_datetime  # You will need this import at the top of the file
from typing import List, Dict, Optional, Any

import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import init_db
from models import Season, Race  # Import the necessary models


# --- Function to Get Event Main Groups (Town-Events/Races) ---

def get_races(season_number: int, max_retries: int = 3) -> Optional[List[Dict[str, str]]]:
    """
    Fetches the list of all 'Event Main Groups' (Town-Events/Races) for a specified HYROX season.
    (Your provided function, slightly cleaned up)
    """

    BASE_URL = f"https://results.hyrox.com/season-{season_number}/index.php"
    params = {
        'content': 'ajax2',
        'func': 'getSearchFields',
        'options[lang]': 'EN_CAP',
        'options[pid]': 'start'
    }

    # print(f"  Fetching events for Season {season_number}...")

    for attempt in range(max_retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=20)
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
                        # The ID from the site, e.g., '2025 Stuttgart'
                        'site_id': event_data['v'][0],
                        'name': event_data['v'][1]  # e.g., '2025 Stuttgart'
                    })

            # print(f"  ✅ Found {len(extracted_events)} events.")
            return extracted_events

        except requests.exceptions.Timeout:
            time.sleep(5)
        except requests.exceptions.HTTPError as errh:
            if response.status_code >= 500:
                time.sleep(5)
                continue
            print(f"  ❌ Permanent HTTP Error (Season {season_number}). Error: {errh}")
            return None
        except (requests.exceptions.RequestException, json.JSONDecodeError) as err:
            print(f"  ❌ Non-recoverable error during fetch: {err}")
            return None

    return None


# --- New Function: Extract Metadata from Race Name ---

def parse_race_metadata(race_name: str) -> Dict[str, Any]:
    """
    Parses a HYROX race name (e.g., '2025 Stuttgart') into city and year/date.

    NOTE: The site IDs are not purely city names, they often include the year.
    Example: '2025 Stuttgart' -> City: Stuttgart, Year: 2025
    """

    data = {
        'city': None,
        'year': None,
        'date_start': None,  # Placeholder for precise date
        # Country/Region cannot be reliably determined from this string alone.
    }

    # Pattern to find a 4-digit year followed by one or more words
    match = re.match(r'(\d{4})\s*(.+)', race_name)
    if match:
        data['year'] = int(match.group(1))
        data['city'] = match.group(2).strip()
    else:
        # Simple split fallback if the year pattern fails
        parts = race_name.split()
        data['city'] = parts[-1] if parts else race_name

    # We set date_start to a placeholder date (e.g., Jan 1st of the year)
    # as the exact date is not provided in this API response.
    if data['year']:
        try:
            data['date_start'] = dt_datetime(data['year'], 1, 1)
        except ValueError:
            pass  # Keep it as None if date construction fails

    return data


# --- New Function: Update Races in DB ---

def update_races_in_db(session: Session, season_data: Dict[str, Any], race_groups: List[Dict[str, str]]):
    """
    Inserts or updates Race records for a given Season.
    """
    season_db_id = season_data.id
    season_number = season_data.number
    insert_count = 0
    update_count = 0

    try:
        for race_group in race_groups:
            race_name = race_group['name']
            metadata = parse_race_metadata(race_name)

            # Use the race name and season_id to check for existence
            # This combination acts as a unique identifier for the event.
            existing_race = session.query(Race).filter(
                Race.name == race_name,
                Race.season_id == season_db_id
            ).first()

            if existing_race:
                # 1. Update existing race data
                existing_race.city = metadata['city']
                existing_race.date_start = metadata['date_start']
                # Add site_id to the existing race if you add a corresponding column
                session.add(existing_race)
                update_count += 1
            else:
                # 2. Insert new race
                new_race = Race(
                    name=race_name,
                    city=metadata['city'],
                    date_start=metadata['date_start'],
                    season_id=season_db_id,
                    # Add site_id if you add a column
                    # site_id=race_group['site_id'],

                    # Set default flags defined in your model
                    is_world_championship=0,
                    is_regional_championship=0,
                    is_national_championship=0
                )
                session.add(new_race)
                insert_count += 1

        session.add(season_data)
        session.commit()
        print(
            f"  ✅ Season {season_number}: Processed {len(race_groups)} events. Inserted: {insert_count}, Updated: {update_count}.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"  ❌ Database error processing Season {season_number}: {e}")


# --- Main Execution ---

if __name__ == '__main__':
    print("=" * 60)
    print("🏁 HYROX Race Scraper: Populating Races from Database Seasons 🏁")
    print("=" * 60)

    # 1. Initialize DB and get session
    session = init_db()

    # 2. Get all seasons from the DB
    try:
        db_seasons = session.query(Season).order_by(Season.number.asc()).all()
    except SQLAlchemyError as e:
        print(f"❌ Error querying seasons from DB: {e}")
        db_seasons = []

    if not db_seasons:
        print("❌ No seasons found in the database. Please run the season update script first.")
        session.close()
        exit()

    print(f"✅ Found {len(db_seasons)} season(s) in the database to process.")

    # 3. Loop through each season and scrape its races
    for season in db_seasons:
        season_number = season.number
        print(f"\n🚀 Processing Season {season_number} (DB ID: {season.id})...")

        # Check if the season was updated very recently (within last 2 minutes). If so, skip to avoid redundant work.

        seconds_since_last_update = (dt_datetime.now() - season.last_updated).total_seconds()
        print(f"  ⏱️ Time since last update: {int(seconds_since_last_update)} seconds.")
        if seconds_since_last_update < 120:
            print(f"  ⏭️ Season {season_number} was updated recently. Skipping to avoid redundancy.")
            continue

        # Scrape all 'Event Main Groups' (Races) for this season
        race_groups = get_races(season_number)

        if race_groups:
            # Update the database with the scraped races for this season
            update_races_in_db(session, season, race_groups)
        else:
            print(f"  ⚠️ No race groups found or request failed for Season {season_number}. Skipping.")

        time.sleep(5)  # Be polite between season requests

    session.close()
    print("\n" + "=" * 60)
    print("✨ Race extraction complete.")
    print("=" * 60)
