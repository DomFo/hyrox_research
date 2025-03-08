from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db import Base
from models.associations import race_divisions


class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id', ondelete="CASCADE"), nullable=False)
    season = relationship("Season", back_populates="races")
    # Many-to-many: a race can have multiple divisions,
    # and a division can appear in multiple races.
    divisions = relationship(
        "Division",
        secondary=race_divisions,
        back_populates="races",
        lazy="dynamic"
    )
    # A race has many results.
    results = relationship("Result", back_populates="race", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Race {self.name}>"
