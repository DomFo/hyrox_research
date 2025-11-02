import re
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import init_db
from models import Season


# --- 1. Scraper Function: Get and Parse Seasons ---

def scrape_hyrox_seasons() -> List[Dict[str, Any]]:
    """
    Fetches the list of all available HYROX seasons by scraping the dropdown menu.

    :return: A list of dictionaries, each containing 'name', 'number', and 'url'.
    """
    # Use a known season page to get the dropdown
    url = "https://results.hyrox.com/season-1/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }

    print("\n1. 🔎 Attempting to scrape all available seasons...")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching seasons URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    scraped_seasons = []

    # Locate the dropdown menu for seasons
    season_menu = soup.find('ul', class_='dropdown-menu')

    if season_menu:
        for anchor in season_menu.find_all('a', href=True):
            relative_url = anchor.get('href')
            season_name = anchor.get_text(strip=True)

            # Use regex to reliably extract the season number from the URL part
            match = re.search(r'season-(\d+)', relative_url)
            season_num = int(match.group(1)) if match else None

            # Construct the full URL
            full_url = f"https://results.hyrox.com{relative_url}"

            if season_num:
                scraped_seasons.append({
                    'name': season_name,
                    'number': season_num,
                    'url': full_url
                })

    print(f"✅ Scraped {len(scraped_seasons)} season(s).")
    return scraped_seasons


# --- 2. Database Update Function ---

def update_seasons_in_db(session: Session,
                         seasons_data: List[Dict[str, Any]],
                         overwrite_existing: bool = False,
                         ):
    """
    Inserts new seasons or updates existing ones using session.merge().

    :param session: The SQLAlchemy Session object.
    :param seasons_data: List of dictionaries containing season data.
    :param overwrite_existing: If True, existing seasons will be updated with new data.
    """
    print("\n2. 💾 Updating/Inserting Seasons into the Database...")

    if not seasons_data:
        print("⚠️ No season data provided. Skipping database update.")
        return

    insert_count = 0
    update_count = 0

    try:
        for data in seasons_data:
            # Check if the season already exists by its unique 'number'
            existing_season = session.query(Season).filter_by(number=data['number']).first()
            if not overwrite_existing and existing_season:
                continue

            if existing_season:
                # Update existing season's data
                existing_season.name = data['name']
                existing_season.results_url = data['url']
                session.add(existing_season)
                update_count += 1
            else:
                # Create and insert new season
                new_season = Season(
                    name=data['name'],
                    number=data['number'],
                    results_url=data['url']
                )
                session.add(new_season)
                insert_count += 1

        # Commit all changes at once
        session.commit()
        print(f"✅ Successfully processed {len(seasons_data)} seasons.")
        print(f"   - {insert_count} new season(s) inserted.")
        print(f"   - {update_count} existing season(s) updated.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Database error occurred: {e}")
    finally:
        session.close()


# --- Demo Functions (For verification) ---

def list_seasons(session: Session):
    """Lists all seasons currently in the database."""
    print("\n3. 📋 Listing all Seasons currently in the DB (Verification):")
    seasons = session.query(Season).order_by(Season.number.asc()).all()
    if not seasons:
        print("   - Database contains no seasons.")
        return

    for season in seasons:
        # Use .count() on the 'dynamic' relationship to check the number of races
        print(f"   - Season {season.number}: {season.name} | Races: {season.races.count()}")


# --- Main Execution ---

if __name__ == '__main__':
    # 1. Initialize DB and get session
    session = init_db()

    # 2. Scrape the data
    scraped_seasons = scrape_hyrox_seasons()

    # 3. Update the database
    # Note: We pass the session to the update function, which closes it.
    update_seasons_in_db(session, scraped_seasons)

    # 4. Re-establish session for verification
    session = init_db()

    # 5. Verify the results
    list_seasons(session)
    session.close()
