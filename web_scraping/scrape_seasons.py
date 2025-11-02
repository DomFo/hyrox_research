from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Session

from models import Season
from web_scraping.util import get_selenium_driver


def scrape_seasons(session: Session) -> List[Season]:
    driver = get_selenium_driver(url="https://results.hyrox.com/")

    try:
        # NavBar with season and language dropdowns
        nav_bar_ul = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.navbar-nav.navbar-right"))
        )

        season_dropdown = nav_bar_ul.find_element(By.CSS_SELECTOR, "li.dropdown.views").find_element(By.CSS_SELECTOR,
                                                                                                     "ul.dropdown-menu")

        season_links = season_dropdown.find_elements(By.TAG_NAME, "a")
        season_data = []
        for link in season_links:
            season = dict()
            href = link.get_attribute("href")
            season_title = link.get_attribute("textContent").strip()  # using textContent instead of .text
            season['name'] = season_title
            season['number'] = href.split("season-")[-1]
            season['url'] = href
            season_data.append(season)
    finally:
        driver.quit()
    sorted_season_data = sorted(season_data, key=lambda x: int(x["number"]))
    add_seasons_to_db(session, sorted_season_data)

    db_seasons = session.query(Season).all()

    return db_seasons


def add_seasons_to_db(session: Session, seasons_list: list[dict]):
    for season_data in seasons_list:
        print(f"Adding season to DB: {season_data['name']}")
        existing_season = session.query(Season).filter(Season.name == season_data['name'])
        if existing_season.count() > 0:
            print(f"Season already exists: {season_data['name']}")
            continue
        try:
            season_db_entry = Season(name=season_data['name'],
                                     number=season_data['number'],
                                     results_url=season_data['url'])
            session.add(season_db_entry)
        except UniqueConstraint as e:
            print(f"Season already exists: {season_data['name']} ({e})")
    session.commit()
