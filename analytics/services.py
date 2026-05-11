import numpy as np
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List
from .models import ExchangeRate
from .schemas import DataPoint, CurrencySeries, AnalyticsResponse


class VolatilityService:
    """
    Handles time-series calculations including Log-Returns
    and Rolling Standard Deviation (Volatility).
    """

    # Visual configuration for the frontend
    COLORS: Dict[str, str] = {
        "IMP": "#2c3e50",  # Deep Blue
        "KER": "#f1c40f",  # Yellow
        "SOV": "#e74c3c",  # Red
    }

    @classmethod
    def get_series(cls, code: str) -> CurrencySeries:
        """
        Calculates volatility and structures data for a specific currency.
        """

        # Fetch from postgres
        records = ExchangeRate.objects.filter(currency_type=code).order_by("date")
        if not records:
            return CurrencySeries(
                label=code, color=cls.COLORS.get(code, "#000000"), points=[]
            )

        # Need at least 2 points to calculate returns/volatility
        if records.count() < 2:
            return CurrencySeries(
                label=dict(ExchangeRate.CURRENCY_TYPES).get(code, code),
                color=cls.COLORS.get(code, "#000000"),
                points=[
                    DataPoint(
                        date=r.date,
                        value=r.value_in_gold,
                        volatility=0,
                        is_milestone=r.is_milestone,
                    )
                    for r in records
                ],
            )
        # Convert Decimal values to float for NumPy compatibility
        values = np.array([r.value_in_gold for r in records], dtype=np.float64)

        # Epsilon safeguard. Replace 0 or negative with a tiny float
        # This prevents np.log(0) which returns -inf
        epsilon = 1e-12
        values = np.where(values <= 0, epsilon, values)

        # Calculate logarithmic rate of change (i.e. velocity of devaluation)
        log_values = np.log(values)
        log_returns = np.diff(log_values)
        log_returns = np.insert(log_returns, 0, 0.0)

        # Calculate rolling volatility (standard deviation of returns)
        # We use a 5-point window to identify shocks
        window = 5
        volatilities = []
        for i in range(len(log_returns)):
            start_idx = max(0, i - window + 1)
            window_slice = log_returns[start_idx : i + 1]
            volatilities.append(float(np.std(window_slice)))

        # Map to pydantic DataPoint objects
        points: List[DataPoint] = []
        for idx, r in enumerate(records):
            safe_val = r.value_in_gold
            print(r.value_in_gold, safe_val)
            points.append(
                DataPoint(
                    date=r.date,
                    value=safe_val,
                    volatility=float(volatilities[idx]),
                    is_milestone=r.is_milestone,
                    event_name=r.event_name or "",
                )
            )

        # Get the human-readable label from the Model choices
        label = dict(ExchangeRate.CURRENCY_TYPES).get(code, code)

        return CurrencySeries(
            label=label,
            color=cls.COLORS.get(code, "#000000"),
            points=points,
        )

    @classmethod
    def run_full_analysis(cls) -> AnalyticsResponse:
        return AnalyticsResponse(
            imperial=cls.get_series("IMP"),
            kerenski=cls.get_series("KER"),
            sovznak=cls.get_series("SOV"),
        )


# class DataUtility:
#     @staticmethod
#     def interpolate_points(
#         start_date: date, end_date: date, start_val: float, end_val: float
#     ) -> List[Tuple[date, float]]:
#         """
#         Creates weekly bridge points between two historical milestones
#         Follows PEP8 naming and type-hinting standards.
#         """
#         days_diff = (end_date - start_date).days
#         if days_diff <= 7:
#             return []
#
#         # Weekly steps
#         weeks = days_diff // 7
#         interpolated = []
#
#         # Linear interpolation of values
#         values = np.linspace(start_val, end_val, weeks + 2)[1:-1]
#
#         for i, val in enumerate(values):
#             bridge_date = start_date + timedelta(weeks=i + 1)
#             interpolated.append((bridge_date, float(val)))
#
#         return interpolated
