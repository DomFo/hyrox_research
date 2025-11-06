import requests

from db import init_db
from models import Race
from models.division import Gender, DivisionName


def make_form_data(race_name: str = "",
                   division_event_id: str = "",
                   ranking: str = "time_finish_netto",
                   sex: str = "",
                   age_class: str = "%") -> dict:
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
        'num_results': '25',
        'submit': ''
    }


def get_search_url(season_number: int) -> str:
    return f"https://results.hyrox.com/season-{season_number}/?pid=list&pidp=ranking_nav"


def example_scrape_results(race_name: str,
                           division_name: DivisionName,
                           gender: Gender):
    # Example usage
    session = init_db()
    race = session.query(Race).filter(Race.name == race_name).first()
    if not race:
        raise Exception(f"Race '{race_name}' not found")
    named_divisions = race.divisions.filter_by(division=division_name).all()
    if len(named_divisions) == 0:
        raise Exception(f"Division '{division_name}' not found in race '{race_name}'")
    division = [div for div in named_divisions if div.gender == gender][0]
    if not division:
        raise Exception(f"Division '{division_name}' with gender '{gender}' not found in race '{race_name}'")
    url = get_search_url(race.season.number)
    form_data = make_form_data(race_name=race_name,
                               division_event_id=division.event_id)

    print(f"URL: {url}")
    print(f"Form Data: {form_data}")
    response = requests.post(url, data=form_data)
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}")  # Print first 500 characters of the response text


if __name__ == '__main__':
    example_scrape_results(
        race_name="2019 Nürnberg",
        division_name=DivisionName.HYROX_PRO,
        gender=Gender.MEN)
