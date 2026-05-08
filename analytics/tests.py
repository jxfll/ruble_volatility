from decimal import Decimal
from datetime import date
from django.test import TestCase
from .models import ExchangeRate
from .services import VolatilityService


class VolatilityMathTest(TestCase):
    def setUp(self):
        # Scenario: Exponential collapse (1.0 -> 0.1 -> 0.01)
        # Mathematically, the log-return is constant here: ln(0.1/1) = ln(0.01/0.1)
        self.data = [
            (date(1917, 1, 1), 1.0, "Start"),
            (date(1917, 1, 2), 0.1, "First Crash"),
            (date(1917, 1, 3), 0.01, "Second Crash"),
        ]
        for dt, val, name in self.data:
            ExchangeRate.objects.create(
                date=dt,
                currency_type="IMP",
                value_in_gold=Decimal(str(val)),
                is_milestone=True,
                event_name=name,
            )

    def test_mathematical_consistency(self):
        """
        Verifies that constant exponential decay results in consistent volatility.
        """
        series = VolatilityService.get_series("IMP")

        # Volatility at index 1 and 2 should be nearly identical
        # because the percentage drop (90%) is the same.
        vol1 = series.points[1].volatility
        vol2 = series.points[2].volatility

        # Use almostEqual for floating point comparisons
        self.assertAlmostEqual(vol1, vol2, places=5)
        self.assertGreater(vol1, 1.0)  # 90% drop is huge volatility

    def test_zero_value_resilience(self):
        """
        Tests that the service handles a total value collapse (0.0) safely.
        """
        ExchangeRate.objects.create(
            date=date(1917, 1, 4),
            currency_type="KER",
            value_in_gold=Decimal("0.0"),
            is_milestone=False,
        )
        # This should not raise ZeroDivisionError or -inf log error
        series = VolatilityService.get_series("KER")
        self.assertEqual(series.points[0].value, 1e-12)  # Check epsilon replacement

    def test_milestone_preservation(self):
        """
        Ensures metadata (event names) passes correctly through the service.
        """
        series = VolatilityService.get_series("IMP")
        first_point = series.points[0]

        self.assertTrue(first_point.is_milestone)
        self.assertEqual(first_point.event_name, "Start")

    def test_pydantic_serialization_readiness(self):
        """
        Verifies the dictionary output matches Pydantic expectations for JSON.
        """
        analysis = VolatilityService.run_full_analysis()
        data = analysis.model_dump(mode="json")

        # Check if the date was serialized to a string correctly (Pydantic V2)
        self.assertIsInstance(data["imperial"]["points"][0]["date"], str)
        self.assertEqual(data["imperial"]["points"][0]["date"], "1917-01-01")
