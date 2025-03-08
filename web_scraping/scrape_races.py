from selenium import webdriver
from sqlalchemy.orm import Session

from models import Season, Race
from web_scraping.util import get_select


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
    season_url = season.results_url
    driver = webdriver.Chrome()
    driver.get(season_url)
    try:
        race_select = get_select(driver, "default-lists-event_main_group", retries=5)
        race_names = [
            opt.text.strip() for opt in race_select.options
            if opt.text.strip() and not opt.get_attribute("disabled") and not opt.text.strip().startswith("Alle")
        ]
        add_races_to_db(session=session, race_names=race_names, season_id=season.id)

    finally:
        driver.quit()
