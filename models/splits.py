from sqlalchemy import Column, Integer, String, Time, Interval, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


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
