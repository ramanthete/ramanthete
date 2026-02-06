# Petrol Pump Daily Operations Management System

A production-oriented Python 3 console application for daily personal use by a petrol pump manager.

## Key capabilities
- Fast, step-by-step daily data entry.
- Supports multiple fuel types and multiple nozzles per fuel.
- Computes:
  - fuel sold per nozzle
  - total sold per fuel
  - expected vs actual closing stock
  - gain/loss by fuel (with clear warnings for losses)
  - total sales volume and value
  - total expenses
  - net cash to deposit
- Prevents negative values and invalid meter sequences.
- Never overwrites prior day files; stores date-based JSON records.
- Generates a clean **Daily Manager Closing Report** in console and JSON.

## Project structure
- `app.py` - entry point
- `petrol_pump_ops/models.py` - domain models and validation
- `petrol_pump_ops/services.py` - report generation logic
- `petrol_pump_ops/storage.py` - file persistence
- `petrol_pump_ops/ui.py` - interactive data entry + report display
- `sample_data/sample_daily_input.json` - sample input data
- `sample_data/example_daily_manager_closing_report.json` - example output report

## Run
Interactive mode:
```bash
python3 app.py
```

Non-interactive mode with sample input:
```bash
python3 app.py --input-file sample_data/sample_daily_input.json
```

Saved files are created automatically under:
- `data/daily_inputs/`
- `data/daily_reports/`

## Future-ready architecture
The modular design allows adding new modules later (attendance & salary, fraud detection, inventory, exports, dashboards/web app) without rewriting the core domain/report logic.
