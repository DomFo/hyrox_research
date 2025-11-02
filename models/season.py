from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from db import Base


class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    number = Column(Integer, nullable=False, unique=True, index=True)
    results_url = Column(String(255), nullable=False, unique=True)
    # One season can have many races
    races = relationship('Race', back_populates='season', lazy='dynamic', cascade='all, delete-orphan')
    last_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.now,  # Set creation time on insert
        onupdate=datetime.now  # Automatically set update time on every edit/flush
    )

    def __repr__(self):
        return f'<Season {self.name} ({self.number}) - {self.results_url} (last updated: {self.last_updated})>'

    def get_by_number(session, number: int) -> 'Season | None':
        return session.query(Season).filter(Season.number == number).first()
