from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db import Base


class Division(Base):
    __tablename__ = 'divisions'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    gender = Column(String, nullable=False)
    # Relationship back to races via the association table
    races = relationship(
        "Race",
        secondary="race_divisions",
        back_populates="divisions"
    )
    # A division has many results.
    results = relationship("Result", back_populates="division", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Division {self.name} ({self.gender})>"
