import concurrent.futures
from time import sleep
from datetime import datetime, timedelta


from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from web_scraping.classes import Split


def get_select(driver, select_id, retries=5, timeout=10):
    for _ in range(retries):
        try:
            elem = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, select_id))
            )
            if elem.tag_name.lower() == "select":
                return Select(elem)
        except StaleElementReferenceException:
            sleep(0.5)
    raise TimeoutException(f"Could not get select element with id '{select_id}' after {retries} retries.")


def make_split_from_row(row) -> Split:
    split_name = row.find_element(By.TAG_NAME, "th").text
    times = row.find_elements(By.TAG_NAME, "td")

    time_of_day = datetime.strptime(times[0].text, "%H:%M:%S")
    elapsed_time = datetime.strptime(times[1].text, "%H:%M:%S")
    time_diff_as_datetime = datetime.strptime(times[2].text, "%M:%S")
    time_diff =timedelta(hours=time_diff_as_datetime.hour, minutes=time_diff_as_datetime.minute, seconds=time_diff_as_datetime.second)
    split = Split(
        split_name=split_name,
        time_of_day=time_of_day.time(),
        time=elapsed_time.time(),
        time_diff=time_diff
    )
    return split
    


def analyze_splits(right_div):
    table_body = right_div.find_element(By.TAG_NAME, "tbody")
    table_body_rows = table_body.find_elements(By.TAG_NAME, "tr")
    for row in table_body_rows:
        split = make_split_from_row(row)
        print(split)
    foo = 1

def analyze_details(left_div):
    foo = 1

def analyze_individual_result_page(driver):

    left_div = driver.find_element(By.CSS_SELECTOR, "div.detail-channel.channel-left")  # col col-xs-12 col-md-6 detail-channel channel-left
    right_div = driver.find_element(By.CSS_SELECTOR, "div.detail-channel.channel-right")  # col col-xs-12 col-md-6 detail-channel channel-right
    analyze_splits(right_div)
    analyze_details(left_div)


    detail_div = driver.find_element(By.CSS_SELECTOR, "div.detail")
    detail_div.find_elements(By.TAG_NAME, "h2")[0].text



def analyze_result_list_item(driver, li):
    links = li.find_elements(By.TAG_NAME, "a")
    if len(links) == 0:
        # header row
        return
    links[0].click()
    sleep(1)
    analyze_individual_result_page(driver)
    driver.back()



def get_results(driver):
    sleep(1)
    results_ul = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group.list-group-multicolumn"))
    )
    # results_lis = results_ul.find_elements(By.CSS_SELECTOR, "li.list-group-item.row")
    # results_lis = results_ul.find_elements(By.XPATH, ".//li[@class='list-group-item row']")
    # results_lis = results_ul.find_elements(
    #     By.XPATH,
    #     ".//li[contains(concat(' ', normalize-space(@class), ' '), ' list-group-item ') and contains(concat(' ', normalize-space(@class), ' '), ' row ')]"
    # )

    results_lis = results_ul.find_elements(
        By.XPATH,
        ".//li[contains(@class, 'list-group-item') and contains(@class, 'row') and not(.//div[contains(@class, 'alert')])]"
    )
    if len(results_lis) <= 1:
        print("No results found.")
        return []

    for li in results_lis:
        analyze_result_list_item(driver, li)



def loop_sex_divisions(driver, sexes):
    for sex in sexes:
        print(f"Selecting sex-division: {sex}")

        div_select_sex = get_select(driver, "default-lists-sex", retries=5)
        confirm_sexes = [opt.text.strip() for opt in div_select_sex.options if opt.text.strip()]
        if sex not in confirm_sexes:
            continue

        div_select_sex.select_by_visible_text(sex)
        sleep(1)
        select_num_results = get_select(driver, "default-num_results", retries=5)
        select_num_results.select_by_visible_text("100")
        sleep(1)
        submit_button = driver.find_element(By.ID, "default-submit")
        submit_button.click()
        restults = get_results(driver)
        driver.back()


def loop_divisions(driver, divisions):
    for division in divisions:
        # Skipping "Adaptive" divisions for now, because they have different structure
        # TODO: Change this as soon as I figured out how to handle the case
        if "adaptive" in division.lower():
            continue
        print(f"Selecting division: {division}")
        select = get_select(driver, "default-lists-event", retries=5)
        select.select_by_visible_text(division)
        sleep(1)  # Give the UI time to fetch the available Gender options for the selected division
        div_select_sex = get_select(driver, "default-lists-sex", retries=5)
        sexes = [opt.text.strip() for opt in div_select_sex.options if opt.text.strip()]
        print(f"Available Sex divisions: {sexes}\n")
        loop_sex_divisions(driver, sexes)
    return


def select_race(driver, race_name):
    for attempt in range(3):
        try:
            div_select = get_select(driver, "default-lists-event", retries=5)
            divisions = [opt.text.strip() for opt in div_select.options if opt.text.strip()]
            print(f"Race: {race_name}")
            print(f"Available Divisions: {divisions}\n")
            loop_divisions(driver, divisions)
            return
        except StaleElementReferenceException:
            sleep(0.5)
    print(f"Failed to extract details for race: {race_name}")


def get_season_events(season_tuple):
    season_title, season_url = season_tuple
    driver = webdriver.Chrome()
    driver.get(season_url)
    try:
        race_select = get_select(driver, "default-lists-event_main_group", retries=5)
        race_names = [
            opt.text.strip() for opt in race_select.options
            if opt.text.strip() and not opt.get_attribute("disabled") and not opt.text.strip().startswith("Alle")
        ]
        print(f"Season: {season_title}\nAvailable Races: {race_names}\n")
        for race_name in race_names:
            print(f"Selecting race: {race_name}")
            if "Valencia" in race_name:
                print("SKIPPING VALENCIA!")
                continue
            selected = False
            for attempt in range(5):
                try:
                    sleep(1)
                    race_select = get_select(driver, "default-lists-event_main_group", retries=5)
                    race_select.select_by_visible_text(race_name)
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "default-lists-event"))
                    )
                    selected = True
                    break
                except StaleElementReferenceException:
                    sleep(1.5)
                except Exception as e:
                    print(f"Skipping race: {race_name} ({e})\n")
                    selected = False
                    break
            if not selected:
                print(f"Skipping race due to repeated issues: {race_name}\n")
                continue
            select_race(driver, race_name)
    finally:
        driver.quit()


def get_seasons():
    driver = webdriver.Chrome()
    base_url = "https://results.hyrox.com/"
    driver.get(base_url)
    try:
        # NavBar with season and language dropdowns
        nav_bar_ul = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.navbar-nav.navbar-right"))
        )

        season_dropdown = nav_bar_ul.find_element(By.CSS_SELECTOR, "li.dropdown.views").find_element(By.CSS_SELECTOR,
                                                                                                     "ul.dropdown-menu")

        season_links = season_dropdown.find_elements(By.TAG_NAME, "a")
        seasons = {}
        for link in season_links:
            href = link.get_attribute("href")
            season_title = link.get_attribute("textContent").strip()  # using textContent instead of .text
            if "season-" in href:
                seasons[season_title] = href
    finally:
        driver.quit()
    return seasons


if __name__ == '__main__':
    multiprocess = False
    seasons = get_seasons()  # dict: {season_title: season_url, ...}
    print(seasons)
    season_items = list(seasons.items())

    if not multiprocess:
        # Sequentially process seasons
        for season_item in season_items:
            get_season_events(season_item)
    else:
        # Parallelize processing of seasons using ProcessPoolExecutor
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(get_season_events, season_items)
