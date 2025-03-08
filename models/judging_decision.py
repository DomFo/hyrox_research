from sqlalchemy import Column, Integer, String, Interval, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class JudgingDecision(Base):
    __tablename__ = 'judging_decisions'
    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
    result = relationship("Result", back_populates="judging_decision", uselist=False)

    bonus = Column(Interval, nullable=False)
    penalty = Column(Interval, nullable=False)
    disqualification_reason = Column(String, nullable=False)
    info = Column(String, nullable=False)
