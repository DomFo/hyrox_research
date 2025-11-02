from sqlalchemy.orm import Session

from models import Season, Race
from web_scraping.util import get_select, get_selenium_driver, race_select_id, get_names_from_select


def scrape_races(session: Session):
    seasons = session.query(Season).all()
    for season in seasons:
        scrape_season_races(session, season)


def add_races_to_db(session: Session, race_names: list[str], season_id: int):
    for race_name in race_names:
        existing_race = session.query(Race).filter(Race.name == race_name)
        if existing_race.count() > 0:
            print(f"Rce already exists: {race_name}")
            continue
        print(f"Adding {race_name} to DB")
        new_race = Race(season_id=season_id,
                        name=race_name)
        session.add(new_race)
    session.commit()


def scrape_season_races(session: Session, season: Season):
    driver = get_selenium_driver(url=season.results_url)
    try:
        race_select = get_select(driver, race_select_id, retries=5)
        race_names = get_names_from_select(race_select)
        add_races_to_db(session=session, race_names=race_names, season_id=season.id)

    finally:
        driver.quit()
