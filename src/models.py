from sqlalchemy import Column, DateTime, Float, Integer, String

from src.database.database import Base


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime)
    title = Column(String)
    x_avg_count_in_line = Column(Float)
