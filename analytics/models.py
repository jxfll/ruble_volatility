from django.db import models


class ExchangeRate(models.Model):
    """
    Stores historical exchange rates and significant political milestones.
    """

    CURRENCY_TYPES = [
        ("IMP", "Imperial Ruble"),
        ("KER", "Kerenski Ruble"),
        ("SOV", "Soviet Sovznak"),
    ]

    # Core time-series data
    date = models.DateField(db_index=True)
    currency_type = models.CharField(
        max_length=3, choices=CURRENCY_TYPES, db_index=True
    )

    # Value relative to 1913 gold parity (1.0 = 100%)
    # Using Decimal for high-precision historical finance
    value_in_gold = models.DecimalField(max_digits=25, decimal_places=10)

    # Milestone/Historical context fields
    is_milestone = models.BooleanField(default=False, db_index=True)
    event_name = models.CharField(max_length=255, blank=True, null=True)
    event_description = models.TextField(blank=True, null=True)

    class Meta:
        # Ensures a currency has only one value per day
        unique_together = ("date", "currency_type")
        # Default ordering for time-series analysis
        ordering = ["date"]
        # Composite index for faster multi-line queries
        indexes = [
            models.Index(fields=["currency_type", "date"]),
        ]

    def __str__(self):
        return (
            f"{self.date} | {self.get_currency_type_display()} | {self.value_in_gold}"
        )
