# from sqlalchemy import Column, Integer, Time, ForeignKey
# from sqlalchemy.orm import relationship
#
# from db import Base
#
#
# class WorkoutResult(Base):
#     __tablename__ = 'workout_results'
#     id = Column(Integer, primary_key=True)
#     result_id = Column(Integer, ForeignKey('results.id', ondelete="CASCADE"), nullable=False)
#     result = relationship("Result", back_populates="workout_result", uselist=False)
#
#     running1 = Column(Time, nullable=False)
#     ski_erg = Column(Time, nullable=False)
#     running2 = Column(Time, nullable=False)
#     sled_push = Column(Time, nullable=False)
#     running3 = Column(Time, nullable=False)
#     sled_pull = Column(Time, nullable=False)
#     running4 = Column(Time, nullable=False)
#     burpee_broad_jumps = Column(Time, nullable=False)
#     running5 = Column(Time, nullable=False)
#     row_erg = Column(Time, nullable=False)
#     running6 = Column(Time, nullable=False)
#     farmers_carry = Column(Time, nullable=False)
#     running7 = Column(Time, nullable=False)
#     sandbag_lunges = Column(Time, nullable=False)
#     running8 = Column(Time, nullable=False)
#     wall_balls = Column(Time, nullable=False)
#     rox_zone_time = Column(Time, nullable=False)
#     run_total = Column(Time, nullable=False)
#     best_run_lap = Column(Time, nullable=False)
