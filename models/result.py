from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from db import Base


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)

    # Summary data from table view
    age_group = Column(String, nullable=True)
    rank_overall = Column(Integer, nullable=False)
    rank_age_group = Column(Integer, nullable=False)
    full_name = Column(String, nullable=True)
    nation_abbreviation = Column(String, nullable=True)
    total_time_ms = Column(Integer, nullable=False)
    link_to_detail_page = Column(String, nullable=True)

    # one-to-many relationship with divisions
    division_id = Column(Integer, ForeignKey('divisions.id', ondelete="CASCADE"), nullable=False)
    division = relationship("Division", back_populates="results")

    def __init__(self,
                 age_group: str,
                 rank_overall: int,
                 rank_age_group: int,
                 full_name: str,
                 nation_abbreviation: str,
                 total_time_ms: int,
                 link_to_detail_page: str
                 ):
        self.age_group = age_group
        self.rank_overall = rank_overall
        self.rank_age_group = rank_age_group
        self.full_name = full_name
        self.nation_abbreviation = nation_abbreviation
        self.total_time_ms = total_time_ms
        self.link_to_detail_page = link_to_detail_page
        super().__init__()

    def __repr__(self):
        return (f"<Result {self.full_name} ({self.nation_abbreviation}) - "
                f"Overall Rank: {self.rank_overall}, Age Group: {self.age_group}, "
                f"Age Group Rank: {self.rank_age_group}, "
                f"Total Time: {self.time_ms_to_string(self.total_time_ms)} - "
                f"link: {self.link_to_detail_page}>")

    @classmethod
    def parse_time_ms(cls, time_str: str) -> int:
        """Parse a time string in the format 'HH:MM:SS' or 'MM:SS' into milliseconds."""
        parts = time_str.split(':')
        parts = [int(part) for part in parts]
        if len(parts) == 3:
            hours, minutes, seconds = parts
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = parts
        else:
            raise ValueError(f"Invalid time format: {time_str}")
        total_ms = (hours * 3600 + minutes * 60 + seconds) * 1000
        return total_ms

    @classmethod
    def time_ms_to_string(cls, time_ms: int) -> str:
        """Convert milliseconds to a time string in the format 'HH:MM:SS' or 'MM:SS'."""
        total_seconds = time_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes:02}:{seconds:02}"
