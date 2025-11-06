import requests
from requests import Session

from db import init_db
from models import Race, Season
from models.division import DivisionName, Gender, Division


def make_params(race_name: str = "",
                event: str = "",
                ranking: str = "",
                sex: str = "",
                age_class: str = "",
                nation: str = '') -> dict:
    return {
        'content': 'ajax2',
        'func': 'getSearchFields',
        'options[b][lists][event_main_group]': f'{race_name}',
        'options[b][lists][event]': f'{event}',
        'options[b][lists][ranking]': f'{ranking}',
        'options[b][lists][sex]': f'{sex}',
        'options[b][lists][age_class]': f'{age_class}',
        'options[b][lists][nation]': f'{nation}',
        'options[lang]': 'EN_CAP',
        'options[pid]': 'start'
    }


def get_base_url(season_number: int) -> str:
    return f"https://results.hyrox.com/season-{season_number}/index.php"


def get_events_from_response(json_response: dict) -> list:
    events = json_response.get('branches', {}).get('lists', {}).get('fields', {}).get('event', {}).get('data', [])
    return events


def get_sexes_from_response(json_response: dict) -> list:
    sexes = json_response.get('branches', {}).get('lists', {}).get('fields', {}).get('sex', {}).get('data', [])
    return sexes


def get_events(season_number: int, race_name: str) -> list:
    # 1. Define the target URL
    base_url = get_base_url(season_number)

    # 2. Define the parameters as a Python dictionary.
    # The 'options[...]' structure from the URL is mapped to nested dictionaries in 'params'.
    # requests handles the proper encoding (e.g., [b] becomes %5Bb%5D) for the URL.
    params = make_params(race_name=race_name)

    # 3. Send the GET request
    try:
        response = requests.get(base_url, params=params)

        # 4. Check if the request was successful
        response.raise_for_status()

        # 5. Get the "events" from the JSON response
        json = response.json()
        events = get_events_from_response(json)

        # print("\n--- Extracted Events ---\n")
        # for event in events:
        #     id = event.get('v')[0]
        #     name = event.get('v')[1]
        #     print(f"Event ID: {id}, Event Name: {name}")

    except requests.exceptions.HTTPError as errh:
        print(f"❌ HTTP Error: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"❌ An error occurred: {err}")

    return events


def make_divisions(season_number: int,
                   race: Race,
                   events: list,
                   session: Session):
    # 1. Loop over all events to get divisions
    for event in events:
        event_name = event.get('v')[1]
        event_id = event.get('v')[0]
        base_url = get_base_url(season_number)
        params = make_params(race_name=race.name,
                             event=event_id,
                             sex='M'
                             )
        # 3. Send the GET request
        try:
            response = requests.get(base_url, params=params)
            # Check if the request was successful
            response.raise_for_status()
            # extract sexes from the JSON response
            json = response.json()
            sexes = get_sexes_from_response(json)
            division_name = DivisionName.from_string(event_name)
            if not division_name:
                continue
            for sex in sexes:
                sex_name = sex.get('v')[1]
                gender = Gender.from_string(sex_name)
                if not gender:
                    continue
                if not Division.valid_combination(division_name, gender):
                    print(f"Invalid combination: {division_name} + {gender}")
                    continue
                # check if division with division_name and gender already exists for this race
                existing_division = session.query(Division).filter(
                    Division.division == division_name,
                    Division.gender == gender,
                    Division.race_id == race.id).first()
                if existing_division:
                    print(f"Division already exists: {existing_division}")
                    continue
                new_division = Division(
                    division=division_name,
                    gender=gender,
                    race_id=race.id,
                    event_id=event_id
                )
                race.divisions.append(new_division)
                session.add(new_division)
                session.commit()
                print(f"Added: {new_division}")
        except requests.exceptions.HTTPError as errh:
            print(f"❌ HTTP Error: {errh}")
        finally:
            session.commit()


def scrape_divisions(season_number: int,
                     session: Session,
                     race: Race = None):
    if race is not None:
        races = [race]
    else:
        season = session.query(Season).filter(Season.number == season_number).first()
        races = season.races.all()
    for r in races:
        print(f"Scraping divisions for race: {r.name}")
        events = get_events(season_number, r.name)
        events_filtered = filter_events(events)
        make_divisions(season_number, r, events_filtered, session)


def filter_events(events: list) -> list:
    # Filter out daily events if they are present (Multi-day events)
    # Keep only "Overall" events
    # BUT!!! Sometimes, events/divisions have also a weekday in them, when there's only one day of that division...
    filtered_events = []
    # Get all acceptable division names
    possible_divisions = [e.value for e in DivisionName]
    # sort by length descending
    possible_divisions = sorted(possible_divisions, key=len, reverse=True)
    # clean the events list so only exact matches remain
    # this will remove stuff like "HYROX TEAM-CHALLANGE"
    # but keep "HYROX PRO - Overall" and "HYROX PRO - Friday"
    clean_events = []
    for event in events:
        event_name = event.get('v')[1]
        event_name_stripped = event_name.split("-")[0].strip()  # remove anything after a hyphen
        if event_name_stripped not in possible_divisions:
            continue
        clean_events.append(event)
    events = clean_events
    for division in possible_divisions:
        existing_events_for_division = [event for event in events if division in event.get('v')[1]]
        if len(existing_events_for_division) == 0:
            continue
        if len(existing_events_for_division) == 1:
            filtered_events.append(existing_events_for_division[0])
        if len(existing_events_for_division) > 1:
            # look for the "Overall" event
            overall_events = [event for event in existing_events_for_division if "Overall" in event.get('v')[1]]
            if len(overall_events) != 1:
                foo = 1
                raise ValueError(
                    f"Expected exactly one 'Overall' event for division '{division}', but found {len(overall_events)}: {overall_events}")
            filtered_events.append(overall_events[0])
        # remove the events so they don't get queried again
        [events.remove(event) for event in existing_events_for_division]
    return filtered_events


def example_scrape_specific_race(race_name: str):
    session = init_db()
    existing_race = session.query(Race).filter(Race.name == race_name).first()

    # remove existing divisions
    divisions = existing_race.divisions.all()
    print(f"Found {len(divisions)} divisions")
    for division in divisions:
        print(division)
        # remove the division
        session.delete(division)
    session.commit()

    scrape_divisions(season_number=existing_race.season.number,
                     session=session,
                     race=existing_race
                     )

    divisions = existing_race.divisions.all()
    print(f"After scraping, found {len(divisions)} divisions")
    for division in divisions:
        print(division)


def example_scrape_all_for_season(season: int = 8):
    session = init_db()
    scrape_divisions(season_number=season,
                     session=session
                     )


if __name__ == '__main__':
    example_scrape_all_for_season(1)
    # example_scrape_specific_race("2019 Nürnberg")
