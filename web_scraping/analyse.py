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


if __name__ == '__main__':
    session = init_db()
    rank_most_frequent_divisions(session)
