from itertools import product

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Session

from db import Base


class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True)
    division = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    # Relationship back to races via the association table
    races = relationship(
        "Race",
        secondary="race_divisions",
        back_populates="divisions"
    )
    # A division has many results.
    results = relationship("Result", back_populates="division", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Division {self.division} {self.gender}>"


# Possible divisions


# Single/Double/Relay  -  Men/Women/Mixed  -  Regular/Pro  -  Resulting Name

# Hyrox - Men
# Hyrox - Women
def safely_add_division(division: str, gender: str, session: Session):
    existing_division = (session.query(Division).filter((Division.division == division)
                                                        & (Division.gender == gender))
                         .first())
    if existing_division:
        return
    new_division = Division(division=division,
                            gender=gender)
    session.add(new_division)
    return


def create_main_divisions(session: Session):
    divisions_all_genders = ['Hyrox Doubles',
                             'Hyrox Team Relay']
    divisions = divisions_all_genders + ['Hyrox',
                                         'Hyrox Pro',
                                         'Hyrox Pro Doubles',
                                         'Hyrox Elite']

    # 'Hyrox Adaptive']
    genders = ['Men', 'Women']
    for division, gender in product(divisions, genders):
        safely_add_division(division=division, gender=gender, session=session)
    # mixed divisions:
    for division in divisions_all_genders:
        safely_add_division(division=division, gender='Mixed', session=session)
    # elite divisions:

    session.commit()
