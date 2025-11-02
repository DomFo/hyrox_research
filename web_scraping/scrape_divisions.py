from time import sleep

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.orm import Session

from models import Race, Division, Season
from web_scraping.util import get_select, get_selenium_driver, race_select_id, division_select_id, gender_select_id, \
    get_names_from_select


def scrape_divisions(session=Session):
    races = (session.query(Race)
             .join(Race.season)
             .order_by(Season.number.asc())
             .all())
    print(f"Found {len(races)} races in DB")
    for race in races:
        scrape_race_divisions(session, race)
        # break


def scrape_race_divisions(session: Session, race: Race):
    driver = get_selenium_driver(url=race.season.results_url)
    try:
        print(f"Scraping divisions for race: {race.name}")
        race_select = get_select(driver, race_select_id, retries=5)

        race_select.select_by_visible_text(race.name)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, division_select_id)))
        sleep(1)
        division_select = get_select(driver, division_select_id, retries=5)
        division_names = get_names_from_select(division_select)

        for division_name in reversed(division_names):
            print(f"Division: {division_name}")
            division_select = get_select(driver, division_select_id, retries=5)
            division_select.select_by_visible_text(division_name)
            sleep(1.5)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, gender_select_id)))
            try:
                gender_select = get_select(driver, gender_select_id, retries=5)
                genders = get_names_from_select(gender_select)
            except Exception as e:
                print(f"Failed to get genders: {e}")
                continue
            print(f"Gender: {genders}")

            for gender in genders:
                # todo: match the given division name and gender to existing divisions
                available_divisions = session.query(Division).all()
                for available_division in available_divisions:
                    print(available_division.division, division_name)

                # session.query(Division).
                foo = 1
                # existing_division = (session.query(Division).filter((Division.division == division_name)
                #                                                     & (Division.gender == gender))
                #                      .first())
                # if existing_division:
                #     print(f"Division already exists: {division_name} - {gender}")
                #     if existing_division not in race.divisions:
                #         race.divisions.append(existing_division)
                #         session.commit()
                #     else:
                #         print("Division already attached to race.")
                # else:
                #     print(f"Adding {division_name} - {gender} to DB")
                #     new_division = Division(division=division_name, gender=gender)
                #     session.add(new_division)
                #     session.commit()
                #     race.divisions.append(new_division)
                #     session.commit()

        print("Done")
    except StaleElementReferenceException:
        print("StaleElementReferenceException in scrape_divisions")
        sleep(1.5)
    except Exception as e:
        print(f"Failed to scrape divisions: {e}")
        foo = 1

    finally:
        print("Quitting driver")
        driver.quit()
