import csv
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.core.exceptions import NON_FIELD_ERRORS
from django.db import transaction
import numpy as np
from django.core.management.base import BaseCommand
from analytics.models import ExchangeRate


class Command(BaseCommand):
    help = "Seeds database using a CSV file and iterpolates weekly bridge points."

    def add_arguments(self, parser):
        """
        Allows passing the CSV path as an argument.
        """
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the milestones CSV file",
            default="data/milestones.csv",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = Path(options["file"])

        if not file_path.exists():
            self.stderr.write(f"Error: File {file_path} not found.")
            return

        # Clear existing data for a clean slate
        ExchangeRate.objects.all().delete()

        # Group milestones by currency from CSV
        milestones_by_type = {"IMP": [], "KER": [], "SOV": []}

        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Store data in a structured way for interpolation
                milestones_by_type[row["type"]].append(
                    {
                        "date": date.fromisoformat(row["date"]),
                        "value": float(row["value"]),
                        "event": row["event"],
                    }
                )

        # Process and interpolate
        for c_type, m_list in milestones_by_type.items():
            # Sort by date to ensure proper bridge generation
            m_list.sort(key=lambda x: x["date"])

            for i in range(len(m_list)):
                current = m_list[i]

                # Save the milestone itself
                self._save_record(current, c_type, is_milestone=True)

                # Generate bridges until the next milestone
                if i < len(m_list) - 1:
                    self._generate_bridges(current, m_list[i + 1], c_type)
        self.stdout.write(self.style.SUCCESS("Database seeded from CSV."))

    def _save_record(self, data, c_type, is_milestone):
        """
        Helper to create or update DB entries.
        """
        ExchangeRate.objects.get_or_create(
            date=data["date"],
            currency_type=c_type,
            defaults={
                "value_in_gold": Decimal(str(data["value"])),
                "is_milestone": is_milestone,
                "event_name": data["event"] if is_milestone else None,
            },
        )

    def _generate_bridges(self, start, end, c_type):
        """
        Interpolate weekly points between two milestones.
        """
        days_diff = (end["date"] - start["date"]).days
        weeks = days_diff // 7

        if weeks > 0:
            # We use logspace for hyperinflation to prevent staircase effects
            # We use the log of the values, interpolate linearly, then exp() back
            log_start = np.log(float(start["value"]))
            log_end = np.log(float(end["value"]))
            log_values = np.linspace(log_start, log_end, weeks + 2)[1:-1]
            values = np.exp(log_values)

            for j, val in enumerate(values):
                bridge_data = {
                    "date": start["date"] + timedelta(weeks=j + 1),
                    "value": val,
                    "event": None,
                }
                self._save_record(bridge_data, c_type, is_milestone=False)
