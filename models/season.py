from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db import Base


class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    number = Column(Integer, nullable=False, unique=True)
    results_url = Column(String, nullable=False, unique=True)
    # One season can have many races
    races = relationship('Race', back_populates='season', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Season {self.name} ({self.number})>'
