"""Application services for computing reports from domain models."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from .models import DailyOperations


class ReportBuilder:
    """Builds normalized daily closing reports from operational input data."""

    def build_daily_manager_closing_report(self, operations: DailyOperations) -> Dict:
        """Create a report dictionary suitable for JSON export and console printing."""
        fuel_sections: List[Dict] = []
        warnings: List[str] = []

        for record in operations.fuel_records:
            nozzle_breakup = [
                {
                    "nozzle_id": nozzle.nozzle_id,
                    "opening_meter": nozzle.opening_meter,
                    "closing_meter": nozzle.closing_meter,
                    "fuel_sold_liters": nozzle.sold_volume,
                }
                for nozzle in record.nozzles
            ]

            gain_loss = record.gain_loss_liters
            if gain_loss < 0:
                warnings.append(
                    f"WARNING: LOSS detected in {record.fuel_type}: {abs(gain_loss)} liters"
                )

            fuel_sections.append(
                {
                    "fuel_type": record.fuel_type,
                    "price_per_liter": record.price_per_liter,
                    "opening_stock_liters": record.opening_stock_liters,
                    "fuel_received_liters": record.fuel_received_liters,
                    "nozzle_readings": nozzle_breakup,
                    "total_fuel_sold_liters": record.total_sold_liters,
                    "expected_closing_stock_liters": record.expected_closing_stock_liters,
                    "actual_closing_stock_liters": record.closing_stock_actual_liters,
                    "gain_loss_liters": gain_loss,
                    "sales_value": record.total_sales_value,
                }
            )

        return {
            "report_name": "Daily Manager Closing Report",
            "date": operations.date,
            "fuel_summary": fuel_sections,
            "collections": {
                "cash_collected": operations.cash_collected,
                "digital_collected": operations.digital_collected,
                "total_collections": operations.total_collections,
            },
            "expenses": [asdict(exp) for exp in operations.expenses],
            "totals": {
                "total_sales_volume_liters": operations.total_sales_volume_liters,
                "total_sales_value": operations.total_sales_value,
                "total_expenses": operations.total_expenses,
                "net_cash_to_deposit": operations.net_cash_to_deposit,
            },
            "warnings": warnings,
        }
