"""Entry point for Petrol Pump Daily Operations Management System.

Supports:
- Interactive daily input mode (default)
- Input JSON mode (--input-file path/to/file.json)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from petrol_pump_ops.models import DailyOperations, Expense, FuelDayRecord, NozzleReading
from petrol_pump_ops.services import ReportBuilder
from petrol_pump_ops.storage import DataStore
from petrol_pump_ops.ui import ConsoleUI


def build_domain_from_dict(raw_data: Dict) -> DailyOperations:
    """Map raw input dictionary to validated domain objects."""
    fuel_records: List[FuelDayRecord] = []
    for fuel in raw_data["fuel_records"]:
        nozzles = [NozzleReading(**nozzle_data) for nozzle_data in fuel["nozzles"]]
        fuel_records.append(
            FuelDayRecord(
                fuel_type=fuel["fuel_type"],
                opening_stock_liters=fuel["opening_stock_liters"],
                fuel_received_liters=fuel["fuel_received_liters"],
                closing_stock_actual_liters=fuel["closing_stock_actual_liters"],
                price_per_liter=fuel["price_per_liter"],
                nozzles=nozzles,
            )
        )

    expenses = [Expense(**exp) for exp in raw_data.get("expenses", [])]

    return DailyOperations(
        date=raw_data["date"],
        fuel_records=fuel_records,
        cash_collected=raw_data["cash_collected"],
        digital_collected=raw_data["digital_collected"],
        expenses=expenses,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Petrol Pump Daily Operations Management System")
    parser.add_argument(
        "--input-file",
        type=Path,
        help="Optional JSON input file for non-interactive execution.",
    )
    args = parser.parse_args()

    ui = ConsoleUI()
    store = DataStore()

    if args.input_file:
        raw_input = store.load_input_file(args.input_file)
    else:
        raw_input = ui.collect_daily_input()

    daily_ops = build_domain_from_dict(raw_input)
    report = ReportBuilder().build_daily_manager_closing_report(daily_ops)

    input_path, report_path = store.save_daily_files(daily_ops.date, raw_input, report)
    ui.print_report(report)

    print(f"\nSaved input data:  {input_path}")
    print(f"Saved report data: {report_path}")


if __name__ == "__main__":
    main()
