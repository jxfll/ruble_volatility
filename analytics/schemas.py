from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from datetime import date


class DataPoint(BaseModel):
    """
    The smallest unit of data for the chart.
    """

    model_config = ConfigDict(from_attributes=True)

    date: date
    value: float
    volatility: float
    is_milestone: bool
    event_name: Optional[str] = None

    @field_validator("value")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Currency value cannot be negative")
        return v


class CurrencySeries(BaseModel):
    """
    A collection of points representing one line on the chart.
    """

    label: str
    color: str
    points: List[DataPoint]


class AnalyticsResponse(BaseModel):
    """
    The final payload containing all three currency timelines.
    """

    imperial: CurrencySeries
    kerenski: CurrencySeries
    sovznak: CurrencySeries
