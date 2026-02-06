"""Filesystem persistence for input and generated reports.

Data is saved with date-based filenames and never overwritten.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple


class DataStore:
    """Persists daily input and report JSON into structured folders."""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or Path.cwd()
        self.input_dir = self.base_path / "data" / "daily_inputs"
        self.report_dir = self.base_path / "data" / "daily_reports"
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def _unique_path(self, folder: Path, date_str: str, suffix: str) -> Path:
        base_name = f"{date_str}_{suffix}.json"
        candidate = folder / base_name
        if not candidate.exists():
            return candidate

        timestamp = datetime.now().strftime("%H%M%S")
        return folder / f"{date_str}_{suffix}_{timestamp}.json"

    def save_daily_files(self, date_str: str, input_data: Dict, report_data: Dict) -> Tuple[Path, Path]:
        """Save daily input and report as JSON files without overwriting prior history."""
        input_path = self._unique_path(self.input_dir, date_str, "input")
        report_path = self._unique_path(self.report_dir, date_str, "manager_closing_report")

        input_path.write_text(json.dumps(input_data, indent=2), encoding="utf-8")
        report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

        return input_path, report_path

    def load_input_file(self, path: Path) -> Dict:
        """Load daily input from a JSON file for non-interactive execution."""
        return json.loads(path.read_text(encoding="utf-8"))
