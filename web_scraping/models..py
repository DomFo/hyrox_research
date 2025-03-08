import datetime

from sqlalchemy import Column, Integer, String, Time, Interval, ForeignKey
from sqlalchemy.orm import relationship

from web_scraping.db import Base


class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    # One season can have many races
    races = relationship('Race', back_populates='season', lazy='dynamic', cascade='all, delete-orphan')


class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # one-to-many relationship with season
    season_id = Column(Integer, ForeignKey('seasons.id', ondelete="CASCADE"), nullable=False)
    season = relationship("Season", back_populates="races")
    # During one Race, multiple divisions compete.
    divisions = relationship("Division", back_populates="race", cascade="all, delete-orphan")


class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True)
    # one-to-many relationship with race
    race_id = Column(Integer, ForeignKey('races.id', ondelete="CASCADE"), nullable=False)
    race = relationship("Race", back_populates="divisions")

    # attributes of the division
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)

    # one division has many results
    results = relationship("Result", back_populates="division", cascade="all, delete-orphan")


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)

    # one-to-many relationship with division
    division_id = Column(Integer, ForeignKey('divisions.id', ondelete="CASCADE"), nullable=False)
    division = relationship("Division", back_populates="results")

    # one-to-one relationship with person_data
    # person_data_id = Column(Integer, ForeignKey('person_data.id'), nullable=False)
    person_data = relationship("PersonData", back_populates="result", uselist=False)
    # one-to-one relationship with workout_result
    # workout_result_id = Column(Integer, ForeignKey('workout_results.id'), nullable=False)
    workout_result = relationship("WorkoutResult", back_populates="result", uselist=False)
    # one-to-one relationship with judging_decision
    # judging_decision_id = Column(Integer, ForeignKey('judging_decisions.id'), nullable=False)
    judging_decision = relationship("JudgingDecision", back_populates="result", uselist=False)
    # one-to-one relationship with totals
    # totals_id = Column(Integer, ForeignKey('totals.id'), nullable=False)
    totals = relationship("Total", back_populates="result", uselist=False)
    # one result has one split_set
    # split_set_id = Column(Integer, ForeignKey('split_sets.id'), nullable=False)
    split_set = relationship("SplitSet", back_populates="result", uselist=False)


class PersonData(Base):
    __tablename__ = 'person_data'
    id = Column(Integer, primary_key=True)

    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="person_data", uselist=False)

    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    start_number = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    nationality = Column(String, nullable=False)


class WorkoutResult(Base):
    __tablename__ = 'workout_results'
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="workout_result", uselist=False)

    running1 = Column(Time, nullable=False)
    ski_erg = Column(Time, nullable=False)
    running2 = Column(Time, nullable=False)
    sled_push = Column(Time, nullable=False)
    running3 = Column(Time, nullable=False)
    sled_pull = Column(Time, nullable=False)
    running4 = Column(Time, nullable=False)
    burpee_broad_jumps = Column(Time, nullable=False)
    running5 = Column(Time, nullable=False)
    row_erg = Column(Time, nullable=False)
    running6 = Column(Time, nullable=False)
    farmers_carry = Column(Time, nullable=False)
    running7 = Column(Time, nullable=False)
    sandbag_lunges = Column(Time, nullable=False)
    running8 = Column(Time, nullable=False)
    wall_balls = Column(Time, nullable=False)
    rox_zone_time = Column(Time, nullable=False)
    run_total = Column(Time, nullable=False)
    best_run_lap = Column(Time, nullable=False)


class JudgingDecision(Base):
    __tablename__ = 'judging_decisions'
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="judging_decision", uselist=False)

    bonus = Column(Interval, nullable=False)
    penalty = Column(Interval, nullable=False)
    disqualification_reason = Column(String, nullable=False)
    info = Column(String, nullable=False)


class Total(Base):
    __tablename__ = 'totals'
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="totals", uselist=False)

    rank_gender = Column(Integer, nullable=False)
    rank_age_group = Column(Integer, nullable=False)
    finish_time = Column(Time, nullable=False)


class SplitSet(Base):
    __tablename__ = 'split_sets'
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="split_set", uselist=False)
    # one split_set has many splits
    splits = relationship("SplitModel", back_populates="split_set", lazy='dynamic', cascade="all, delete-orphan")


class SplitModel(Base):
    __tablename__ = 'splits'
    id = Column(Integer, primary_key=True)

    split_set_id = Column(Integer, ForeignKey('split_sets.id'), nullable=False)
    split_set = relationship("SplitSet", back_populates="splits")

    split_order = Column(Integer, nullable=False)  # order in which the split occurred
    gate_name = Column(String, nullable=False)  # e.g., 'Rox In', 'Rox Out', etc.
    time_of_day = Column(Time, nullable=False)
    elapsed = Column(Time, nullable=False)  # time since race start
    diff = Column(Interval, nullable=False)  # delta from previous gate


if __name__ == '__main__':
    # Test the models
    from web_scraping.db import init_db

    session = init_db('sqlite:///:memory:')

    # create a season
    season = Season(name="Season 24/25", number=2025)
    session.add(season)
    session.commit()

    # Create a Race
    race = Race(name="Race 2025 Valencia", season=season)
    session.add(race)
    session.commit()

    # Create another Race
    race2 = Race(name="2025 Rome", season=season)
    session.add(race2)
    session.commit()

    # Show all races of the season
    print(season.races.all())

    # Create a Division
    division = Division(name="HYROX PRO", gender="M", race=race)
    session.add(division)
    session.commit()

    # Create a Result
    result = Result(division=division)
    session.add(result)
    session.commit()

    # Create a SplitSet
    split_set = SplitSet(result_id=result.id)
    session.add(split_set)
    session.commit()

    # Create a Split
    split = SplitModel(split_set_id=split_set.id,
                       split_order=1,
                       gate_name="Rox In",
                       time_of_day=datetime.time(8, 0, 0),
                       elapsed=datetime.time(0, 0, 0),
                       diff=datetime.timedelta(0, 0, 0))
    session.add(split)
    session.commit()

    # Create another Split
    split2 = SplitModel(split_set_id=split_set.id,
                        split_order=2,
                        gate_name="Rox Out",
                        time_of_day=datetime.time(8, 5, 0),
                        elapsed=datetime.time(0, 5, 0),
                        diff=datetime.timedelta(0, 5, 0))

    session.add(split2)
    session.commit()

    # Show all splits of the split_set
    print(split_set.splits.all())
