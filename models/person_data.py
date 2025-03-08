from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


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
