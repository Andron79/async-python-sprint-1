from pydantic import BaseModel
from typing import List


class HourDetailModel(BaseModel):
    hour: str
    temp: int
    condition: str


class DateDetailModel(BaseModel):  # TODO
    date: str
    hours: List[HourDetailModel]


class ForecastsDetailModel(BaseModel):
    forecasts: List[DateDetailModel]


class CityDetailModel(BaseModel):
    city: str
    forecast: ForecastsDetailModel
