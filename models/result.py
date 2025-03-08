from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)

    # one-to-many relationship with races
    race_id = Column(Integer, ForeignKey('races.id', ondelete="CASCADE"), nullable=False)
    race = relationship("Race", back_populates="results")

    # one-to-many relationship with divisions
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
