import enum

from sqlalchemy import Column, Integer, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from db import Base


class DivisionName(enum.Enum):
    HYROX = "HYROX"
    HYROX_DOUBLES = "HYROX DOUBLES"
    HYROX_PRO = "HYROX PRO"
    HYROX_PRO_DOUBLES = "HYROX PRO DOUBLES"
    HYROX_TEAM_RELAY = "HYROX TEAM RELAY"
    HYROX_ELITE_15 = "HYROX ELITE 15"
    HYROX_ELITE = "HYROX ELITE"
    HYROX_ELITE_15_DOUBLES = "HYROX DOUBLES ELITE 15"
    HYROX_ADAPTIVE = "HYROX ADAPTIVE"

    @classmethod
    def from_string(cls, input_string: str) -> 'DivisionName | None':
        # TODO: improve matching logic: "HYROX DOUBLES ELITE 15" is sometimes called "HYROX PRO DOUBLES ELITE 15 - Saturday" geez..z
        # find exact matches of enum values contained in the input string
        matches = [role for role in cls if role.value in input_string.upper()]
        # reduce the matches to the longest match
        if matches:
            return max(matches, key=lambda role: len(role.value))
        else:
            return None


class Gender(enum.Enum):
    MEN = 'MEN'
    WOMEN = 'WOMEN'
    MIXED = 'MIXED'

    @classmethod
    def from_string(cls, input_string: str) -> 'DivisionName | None':
        input_string = input_string.upper()
        return next((gender for gender in cls if gender.value == input_string), None)


class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True)
    division = Column(Enum(DivisionName), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    # Relationship back to races via the association table
    race_id = Column(Integer, ForeignKey('races.id', ondelete="CASCADE"), nullable=False)
    race = relationship(
        "Race",
        back_populates="divisions"
    )
    # results.hyrox.com internal event ID for this division
    event_id = Column(String, nullable=True, unique=False)

    # A division has many results.
    results = relationship("Result", back_populates="division", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Division {self.division.value} {self.gender.value} ({self.race.name}, id: {self.event_id})).>"

    @classmethod
    def valid_combination(cls, division, gender) -> bool:
        # ONLY HYROX DOUBLES and HYROX TEAM RELAY can be MIXED
        is_mixed = gender == Gender.MIXED
        is_mixed_division = division in [DivisionName.HYROX_DOUBLES, DivisionName.HYROX_TEAM_RELAY]
        if is_mixed and not is_mixed_division:
            return False
        return True
