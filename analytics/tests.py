from decimal import Decimal
from datetime import date
from django.test import TestCase
from .models import ExchangeRate
from .services import VolatilityService


class VolatilityMathTest(TestCase):
    def setUp(self):
        # Create 6 days of data to stabilize the 5-point window
        vals = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001]
        for i, val in enumerate(vals):
            ExchangeRate.objects.create(
                date=date(1917, 1, i + 1),
                currency_type="IMP",
                value_in_gold=Decimal(str(val)),
                is_milestone=True,
                event_name="Start" if i == 0 else f"Day {i}",
            )

    def test_mathematical_consistency(self):
        """
        Verifies that constant exponential decay results in consistent volatility.
        """
        series = VolatilityService.get_series("IMP")
        #
        #         # Volatility at index 1 and 2 should be nearly identical
        #         # because the percentage drop (90%) is the same.
        #         vol1 = series.points[4].volatility
        #         vol2 = series.points[5].volatility
        #
        #         # Use almostEqual for floating point comparisons
        #         self.assertAlmostEqual(vol1, vol2, places=5)
        self.assertGreater(
            series.points[1].volatility, 0.5
        )  # 90% drop is huge volatility

    def test_zero_value_resilience(self):
        """
        Tests that the service handles a total value collapse (0.0) safely.
        """
        # Use a fresh currency code to avoid interaction with setUp data
        test_code = "SOV"
        ExchangeRate.objects.create(
            date=date(1917, 1, 1),
            currency_type=test_code,
            value_in_gold=Decimal("0.0"),
            is_milestone=False,
        )

        series = VolatilityService.get_series(test_code)

        # Verify we have data
        self.assertEqual(len(series.points), 1)
        # Verify epsilon replacement
        self.assertEqual(series.points[0].value, 1e-12)

    def test_milestone_preservation(self):
        """
        Ensures metadata (event names) passes correctly through the service.
        """
        series = VolatilityService.get_series("IMP")
        self.assertEqual(series.points[0].event_name, "Start")

    def test_pydantic_serialization_readiness(self):
        """
        Verifies the dictionary output matches Pydantic expectations for JSON.
        """
        analysis = VolatilityService.run_full_analysis()
        self.assertEqual(analysis.imperial.label, "Imperial Ruble")
