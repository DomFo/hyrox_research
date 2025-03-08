from sqlalchemy import Column, Integer, Time, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Total(Base):
    __tablename__ = 'totals'
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="totals", uselist=False)

    rank_gender = Column(Integer, nullable=False)
    rank_age_group = Column(Integer, nullable=False)
    finish_time = Column(Time, nullable=False)
