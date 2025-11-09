# from sqlalchemy import Column, Integer, String
#
# from db import Base
#
#
# class AgeGroup(Base):
#     __tablename__ = 'age_groups'
#     id = Column(Integer, primary_key=True)
#     name = Column(String, nullable=False, unique=True)
#     description = Column(String, nullable=True)
#
#     def __repr__(self):
#         return f"<AgeGroup {self.name} - {self.description}>"
