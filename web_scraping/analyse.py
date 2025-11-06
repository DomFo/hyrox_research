from sqlalchemy import func
from sqlalchemy.orm import Session

from db import init_db
from models import *
from models.associations import race_divisions


def rank_most_frequent_divisions(session: Session):
    races = session.query(Race).all()
    divisions = session.query(Division).all()
    div_example = divisions[0]

    divisions = (
        session.query(Division)
        .outerjoin(race_divisions, Division.id == race_divisions.c.division_id)
        .group_by(Division.id)
        .order_by(func.count(race_divisions.c.race_id).desc())
        .all()
    )

    for d in divisions:
        print(d, len(d.races))


def list_seasons(session: Session):
    seasons = session.query(Season).order_by(Season.number.asc()).all()
    for season in seasons:
        print(season)


def list_season_races(session: Session, season_number: int):
    season = session.query(Season).filter(Season.number == season_number).first()
    if not season:
        print(f"No season found with number {season_number}")
        return
    races = session.query(Race).filter(Race.season_id == season.id).order_by(Race.name.asc()).all()
    for race in races:
        print(race)


def list_races(session: Session, season_number: int = None):
    if season_number is not None:
        list_season_races(session, season_number)
    else:
        # if no season number is provided, list all races for all seasons
        seasons = session.query(Season).order_by(Season.number.asc()).all()
        for season in seasons:
            print(f"\nRaces for Season {season.number}: {season.name}")
            list_season_races(session, season.number)


def list_divisions(session: Session, race: Race):
    divisions = session.query(Division).filter(Division.race_id == race.id).order_by(Division.division.asc()).all()
    for division in divisions:
        print(division)


if __name__ == '__main__':
    session = init_db()
    # list_seasons(session)
    # list_races(session)
    # existing_race = session.query(Race).filter(Race.name == '2025 Stuttgart').first()
    # if existing_race:
    #     list_divisions(session, existing_race)
    season = session.query(Season).filter(Season.number == 8).first()
    for race in season.races:
        print(race.name)
        if not "Hamburg" in race.name:
            continue
        print(race.divisions.all())
        for d in race.divisions:
            print(f" - {d}")
        print(f"Number of divisions: {len(race.divisions.all())}")
        # if
    # rank_most_frequent_divisions(session)
    atlanta = session.query(Race).filter(Race.name == '2025 Atlanta').first()
    divisions_atlanta = atlanta.divisions
    for d in divisions_atlanta:
        print(d)
