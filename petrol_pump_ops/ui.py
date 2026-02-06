"""Console input and output helpers for quick daily operations usage."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List



class ConsoleUI:
    """Handles guided 2-3 minute daily data entry flow with validation loops."""

    def prompt_non_negative_float(self, label: str) -> float:
        while True:
            raw = input(f"{label}: ").strip()
            try:
                value = float(raw)
                if value < 0:
                    print("Invalid input. Value cannot be negative. Please re-enter.")
                    continue
                return value
            except ValueError:
                print("Invalid input. Enter a numeric value.")

    def prompt_date(self) -> str:
        while True:
            date_str = input("Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

    def collect_daily_input(self) -> Dict:
        """Collects complete day data interactively."""
        print("\n=== Petrol Pump Daily Operations Entry ===")
        date_str = self.prompt_date()

        fuel_count = int(self.prompt_non_negative_float("Number of fuel types today (e.g., 2)"))
        while fuel_count < 1:
            print("At least one fuel type is required.")
            fuel_count = int(self.prompt_non_negative_float("Number of fuel types today"))

        fuel_records: List[Dict] = []
        for idx in range(1, fuel_count + 1):
            print(f"\n--- Fuel Section {idx} ---")
            fuel_type = input("Fuel type name (e.g., Petrol, Diesel): ").strip() or f"Fuel-{idx}"
            opening_stock = self.prompt_non_negative_float(f"{fuel_type} opening stock (liters)")
            fuel_received = self.prompt_non_negative_float(f"{fuel_type} fuel received (liters)")
            closing_stock = self.prompt_non_negative_float(
                f"{fuel_type} closing stock by dip reading (liters)"
            )
            price_per_liter = self.prompt_non_negative_float(f"{fuel_type} price per liter")

            nozzle_count = int(self.prompt_non_negative_float(f"Number of {fuel_type} nozzles"))
            while nozzle_count < 1:
                print("At least one nozzle is required.")
                nozzle_count = int(self.prompt_non_negative_float(f"Number of {fuel_type} nozzles"))

            nozzles: List[Dict] = []
            for n_idx in range(1, nozzle_count + 1):
                print(f"  Nozzle {n_idx}")
                nozzle_id = input("  Nozzle ID: ").strip() or f"{fuel_type[:3].upper()}-{n_idx}"
                while True:
                    opening_meter = self.prompt_non_negative_float("  Opening meter")
                    closing_meter = self.prompt_non_negative_float("  Closing meter")
                    if closing_meter < opening_meter:
                        print(
                            "  Invalid reading: closing meter cannot be less than opening meter. Re-enter."
                        )
                    else:
                        nozzles.append(
                            {
                                "nozzle_id": nozzle_id,
                                "opening_meter": opening_meter,
                                "closing_meter": closing_meter,
                            }
                        )
                        break

            fuel_records.append(
                {
                    "fuel_type": fuel_type,
                    "opening_stock_liters": opening_stock,
                    "fuel_received_liters": fuel_received,
                    "closing_stock_actual_liters": closing_stock,
                    "price_per_liter": price_per_liter,
                    "nozzles": nozzles,
                }
            )

        print("\n--- Collections ---")
        cash_collected = self.prompt_non_negative_float("Cash collected")
        digital_collected = self.prompt_non_negative_float("Digital payments collected")

        print("\n--- Expenses ---")
        expense_count = int(self.prompt_non_negative_float("Number of expenses"))
        expenses: List[Dict] = []
        for idx in range(1, expense_count + 1):
            description = input(f"Expense {idx} description: ").strip()
            amount = self.prompt_non_negative_float(f"Expense {idx} amount")
            expenses.append({"description": description, "amount": amount})

        return {
            "date": date_str,
            "fuel_records": fuel_records,
            "cash_collected": cash_collected,
            "digital_collected": digital_collected,
            "expenses": expenses,
        }

    def print_report(self, report: Dict) -> None:
        """Render report in a manager-friendly formatted console output."""
        print("\n" + "=" * 64)
        print(f"{report['report_name']} | Date: {report['date']}")
        print("=" * 64)

        for fuel in report["fuel_summary"]:
            print(f"\n[{fuel['fuel_type']}]")
            print(f"  Opening Stock (L):           {fuel['opening_stock_liters']}")
            print(f"  Received During Day (L):     {fuel['fuel_received_liters']}")
            print("  Nozzle Sales:")
            for nozzle in fuel["nozzle_readings"]:
                print(
                    f"    - {nozzle['nozzle_id']}: {nozzle['fuel_sold_liters']} L "
                    f"(Open {nozzle['opening_meter']} -> Close {nozzle['closing_meter']})"
                )
            print(f"  Total Sold (L):              {fuel['total_fuel_sold_liters']}")
            print(f"  Expected Closing Stock (L):  {fuel['expected_closing_stock_liters']}")
            print(f"  Actual Closing Stock (L):    {fuel['actual_closing_stock_liters']}")
            print(f"  Gain/Loss (L):               {fuel['gain_loss_liters']}")
            print(f"  Sales Value (INR):           {fuel['sales_value']}")

        print("\n--- Financial Summary ---")
        totals = report["totals"]
        collections = report["collections"]
        print(f"Total Sales Volume (L):        {totals['total_sales_volume_liters']}")
        print(f"Total Sales Value (INR):       {totals['total_sales_value']}")
        print(f"Cash Collected (INR):          {collections['cash_collected']}")
        print(f"Digital Collected (INR):       {collections['digital_collected']}")
        print(f"Total Expenses (INR):          {totals['total_expenses']}")
        print(f"Net Cash to Deposit (INR):     {totals['net_cash_to_deposit']}")

        if report.get("warnings"):
            print("\n!!! CRITICAL WARNINGS !!!")
            for warning in report["warnings"]:
                print(f"  {warning}")

        print("=" * 64)
