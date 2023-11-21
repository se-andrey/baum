from datetime import datetime

from pydantic import BaseModel


class TextData(BaseModel):
    datetime: str
    title: str
    text: str


class Result(BaseModel):
    datetime: datetime
    title: str
    x_avg_count_in_line: float
