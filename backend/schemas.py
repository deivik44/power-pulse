from pydantic import BaseModel
from datetime import datetime


class ForecastRequest(BaseModel):
    Temperature: float
    Humidity: float
    WindSpeed: float
    GeneralDiffuseFlows: float
    DiffuseFlows: float

    hour: int
    day: int
    day_of_week: int
    month: int

    lag_1: float
    lag_6: float
    lag_24: float
    lag_144: float

class PeakRequest(BaseModel):
    Temperature: float
    Humidity: float
    WindSpeed: float
    GeneralDiffuseFlows: float
    DiffuseFlows: float
    hour: int
    day: int
    day_of_week: int
    month: int
    lag_1: float
    lag_6: float
    lag_24: float
    lag_144: float


class AnomalyRequest(BaseModel):
    Temperature: float
    Humidity: float
    WindSpeed: float
    GeneralDiffuseFlows: float
    DiffuseFlows: float
    hour: int
    day: int
    day_of_week: int
    month: int
    lag_1: float
    lag_6: float
    lag_24: float
    lag_144: float
    actual_consumption: float

class StreamingReading(BaseModel):
    timestamp: datetime
    temperature: float
    humidity: float
    wind_speed: float
    general_diffuse_flows: float
    diffuse_flows: float
    consumption: float