"""Domain models for petrol pump daily operations.

These models are intentionally framework-agnostic to allow future expansion
into analytics, automation workflows, and dashboard backends.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class ValidationError(ValueError):
    """Raised when business validation fails for user-supplied daily data."""


@dataclass
class NozzleReading:
    """Meter readings for a single nozzle during a day."""

    nozzle_id: str
    opening_meter: float
    closing_meter: float

    def __post_init__(self) -> None:
        if self.opening_meter < 0 or self.closing_meter < 0:
            raise ValidationError("Meter readings cannot be negative.")
        if self.closing_meter < self.opening_meter:
            raise ValidationError(
                f"Closing meter cannot be less than opening meter for nozzle {self.nozzle_id}."
            )

    @property
    def sold_volume(self) -> float:
        """Fuel sold by this nozzle in liters."""
        return round(self.closing_meter - self.opening_meter, 3)


@dataclass
class FuelDayRecord:
    """Daily stock and sales record for one fuel type."""

    fuel_type: str
    opening_stock_liters: float
    fuel_received_liters: float
    closing_stock_actual_liters: float
    price_per_liter: float
    nozzles: List[NozzleReading] = field(default_factory=list)

    def __post_init__(self) -> None:
        for value_name, value in (
            ("opening stock", self.opening_stock_liters),
            ("fuel received", self.fuel_received_liters),
            ("closing stock", self.closing_stock_actual_liters),
            ("price per liter", self.price_per_liter),
        ):
            if value < 0:
                raise ValidationError(f"{value_name.title()} cannot be negative for {self.fuel_type}.")
        if not self.nozzles:
            raise ValidationError(f"At least one nozzle is required for {self.fuel_type}.")

    @property
    def total_sold_liters(self) -> float:
        """Total volume sold across all nozzles."""
        return round(sum(nozzle.sold_volume for nozzle in self.nozzles), 3)

    @property
    def expected_closing_stock_liters(self) -> float:
        """Expected closing stock based on stock movement and nozzle sales."""
        return round(
            self.opening_stock_liters + self.fuel_received_liters - self.total_sold_liters,
            3,
        )

    @property
    def gain_loss_liters(self) -> float:
        """Gain/loss value (positive = gain, negative = loss)."""
        return round(self.closing_stock_actual_liters - self.expected_closing_stock_liters, 3)

    @property
    def total_sales_value(self) -> float:
        """Sales value for this fuel type."""
        return round(self.total_sold_liters * self.price_per_liter, 2)


@dataclass
class Expense:
    """Represents one expense entry for the day."""

    description: str
    amount: float

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise ValidationError("Expense description cannot be empty.")
        if self.amount < 0:
            raise ValidationError("Expense amount cannot be negative.")


@dataclass
class DailyOperations:
    """Aggregate day-level operational data and computed business outputs."""

    date: str
    fuel_records: List[FuelDayRecord]
    cash_collected: float
    digital_collected: float
    expenses: List[Expense] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.cash_collected < 0 or self.digital_collected < 0:
            raise ValidationError("Collected amounts cannot be negative.")
        if not self.fuel_records:
            raise ValidationError("At least one fuel record is required.")

    @property
    def total_sales_volume_liters(self) -> float:
        return round(sum(record.total_sold_liters for record in self.fuel_records), 3)

    @property
    def total_sales_value(self) -> float:
        return round(sum(record.total_sales_value for record in self.fuel_records), 2)

    @property
    def total_expenses(self) -> float:
        return round(sum(exp.amount for exp in self.expenses), 2)

    @property
    def total_collections(self) -> float:
        return round(self.cash_collected + self.digital_collected, 2)

    @property
    def net_cash_to_deposit(self) -> float:
        """Net amount after operational expenses; discrepancies are not auto-corrected."""
        return round(self.total_collections - self.total_expenses, 2)

    def gain_loss_by_fuel(self) -> Dict[str, float]:
        """Fuel-wise gain/loss map for diagnostics and reporting."""
        return {record.fuel_type: record.gain_loss_liters for record in self.fuel_records}
