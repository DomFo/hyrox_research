import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy.orm import Session

from db import init_db
from models import Race, Result
from models.division import Gender, DivisionName, Division


def make_form_data(race_name: str = "",
                   division_event_id: str = "",
                   ranking: str = "time_finish_netto",
                   sex: str = "",
                   age_class: str = "%",
                   num_results: int = 100) -> dict:
    return {
        'lang': 'EN_CAP',
        'startpage': 'start_responsive',
        'startpage_type': 'lists',
        'event_main_group': f'{race_name}',
        'event': f'{division_event_id}',
        'ranking': f'{ranking}',
        'search[name]': '',
        'search[firstname]': '',
        'search[sex]': f'{sex}',
        'search[age_class]': f'{age_class}',
        'search[nation]': '%',
        'num_results': f'{num_results}',
        'submit': ''
    }


def get_search_url(season_number: int) -> str:
    return f"https://results.hyrox.com/season-{season_number}/?pid=list&pidp=ranking_nav"


def get_rank_overall(row_soup: Tag) -> int | None:
    tag_rank = 'div'
    class_rank = 'list-field type-place place-primary numeric'
    rank_overall = row_soup.find(tag_rank, {"class": class_rank}).get_text(strip=True)
    if not rank_overall.isdigit():
        return None
    return int(rank_overall)


def get_rank_age_group(row_soup: Tag) -> int | None:
    tag_rank_age_group = 'div'
    class_rank_age_group = 'list-field type-place place-secondary hidden-xs numeric'
    rank_age_group = row_soup.find(tag_rank_age_group, {"class": class_rank_age_group}).get_text(strip=True)
    if not rank_age_group.isdigit():
        return None
    return int(rank_age_group)


def get_nation_abbreviation(row_soup: Tag) -> str:
    tag_nation = "span"
    class_nation = "nation__abbr"
    nation_abbr = row_soup.find(tag_nation, {"class": class_nation}).get_text(strip=True)
    return nation_abbr


def get_fullname(row_soup: Tag) -> str:
    tag_fullname = 'h4'
    class_fullname = 'list-field type-fullname'
    fullname_soup = row_soup.find(tag_fullname, {"class": class_fullname})
    fullname = fullname_soup.get_text(strip=True)
    return fullname


def get_detailed_results_page_link(row_soup: Tag, base_url: str) -> str:
    link = row_soup.find("a").get("href").strip()
    # replace the ?pid=list&... part of the base_url with the link
    link = base_url.split("?pid=")[0] + link
    return link


def get_age_group(row_soup: Tag) -> str:
    tag_age_group = 'div'
    class_age_group = 'list-field type-age_class'
    age_group = row_soup.find(tag_age_group, {"class": class_age_group}).get_text(strip=True)
    age_group = age_group.replace("Age Group", "")
    return age_group


def get_total_time(row_soup: Tag) -> str:
    tag_total_time = 'div'
    class_total_time = 'right list-field type-time'
    total_time = row_soup.find(tag_total_time, {"class": class_total_time}).get_text(strip=True)
    total_time = total_time.replace("Total", "")
    return total_time


def get_workout_time(row_soup: Tag) -> str:
    tag_workout_time = 'div'
    class_workout_time = "rounds list-field type-eval"
    workout_time = row_soup.find(tag_workout_time, {"class": class_workout_time}).get_text(strip=True)
    workout_time = workout_time.replace("Workout", "")
    return workout_time


def parse_row_soup(row_soup: Tag, url: str) -> dict:
    rank_overall = get_rank_overall(row_soup)
    rank_age_group = get_rank_age_group(row_soup)
    fullname = get_fullname(row_soup)
    nation_abbreviation = get_nation_abbreviation(row_soup)

    detailed_results_page_link = get_detailed_results_page_link(row_soup, url)
    age_group = get_age_group(row_soup)
    total_time = get_total_time(row_soup)
    workout_time = get_workout_time(row_soup)

    row_info_dict = {
        "fullname": fullname,
        "nation_abbreviation": nation_abbreviation,
        "rank_overall": rank_overall,
        "rank_age_group": rank_age_group,
        "age_group": age_group,
        "total_time": total_time,
        "workout_time": workout_time,
        "detailed_results_page_link": detailed_results_page_link,
    }
    return row_info_dict


def find_race(session: Session, race_name: str) -> Race:
    race = session.query(Race).filter(Race.name == race_name).first()
    if not race:
        raise Exception(f"Race '{race_name}' not found")
    return race


def find_division(race: Race,
                  division_name: DivisionName,
                  gender: Gender) -> Division:
    named_divisions = race.divisions.filter_by(division=division_name).all()
    if len(named_divisions) == 0:
        raise Exception(f"Division '{division_name}' not found in race '{race.name}'")
    division = [div for div in named_divisions if div.gender == gender][0]
    if not division:
        raise Exception(f"Division '{division_name}' with gender '{gender}' not found in race '{race_name}'")
    return division


def example_scrape_result_summaries(race_name: str,
                                    division_name: DivisionName,
                                    gender: Gender):
    # Example usage to scrape for specific race, division, and gender
    session = init_db()
    race = find_race(session, race_name)
    division = find_division(race, division_name, gender)
    url = get_search_url(race.season.number)
    form_data = make_form_data(race_name=race_name,
                               division_event_id=division.event_id,
                               sex=gender.value[0].upper())

    print(f"URL: {url}")
    print(f"Form Data: {form_data}")
    response = requests.post(url, data=form_data)
    print(f"Response Status Code: {response.status_code}")
    # print(f"Response Text: {response.text[:500]}")  # Print first 500 characters of the response text

    page_soup = BeautifulSoup(response.text, 'html.parser')

    class_table = 'col-sm-12 row-xs'
    tag_table = 'div'
    table_soup = page_soup.find_all(tag_table, {"class": class_table})

    tag_rows = 'li'
    class_rows = 'list-active list-group-item row'
    class_rows_2 = 'list-group-item row'
    rows_soup = table_soup[0].find_all(tag_rows, {"class": class_rows}) + \
                table_soup[0].find_all(tag_rows, {"class": class_rows_2})
    for row_soup in rows_soup:
        row_info = parse_row_soup(row_soup, url)
    print(row_info)
    new_result = make_new_result(row_info)
    division.results.append(new_result)
    session.add(new_result)
    session.commit()


def make_new_result(row_info: dict) -> Result:
    return Result(
        full_name=row_info['fullname'],
        nation_abbreviation=row_info['nation_abbreviation'],
        rank_overall=row_info['rank_overall'],
        rank_age_group=row_info['rank_age_group'],
        age_group=row_info['age_group'],
        total_time_ms=Result.parse_time_ms(row_info['total_time']),
        workout_time_ms=Result.parse_time_ms(row_info['workout_time']),
        link_to_detail_page=row_info['detailed_results_page_link'],
    )


def example_print_result_summaries(race_name: str,
                                   division_name: DivisionName,
                                   gender: Gender):
    # Example usage
    session = init_db()
    race = find_race(session, race_name)
    division = find_division(race, division_name, gender)
    # results = division.results.all()
    results = session.query(Result).filter(division == division).all()
    for result in results:
        print(result)


if __name__ == '__main__':
    # example_scrape_result_summaries(
    #     race_name="2019 Nürnberg",
    #     division_name=DivisionName.HYROX_PRO,
    #     gender=Gender.MEN)

    example_print_result_summaries(race_name="2019 Nürnberg",
                                   division_name=DivisionName.HYROX_PRO,
                                   gender=Gender.MEN)
