# Stock Market Data Collection

This project collects, preprocesses, and saves historical stock index data for:

- NSE Nifty 50
- BSE Sensex

The repository includes:

- `Stock_market.ipynb` for notebook-based exploration
- `stock_pipeline.py` for a repeatable script-based run
- raw fallback CSV files: `nse.csv` and `bse.csv`
- cleaned output files inside `stock_data/`

## How It Works

The pipeline tries data sources in this order:

1. Alpha Vantage, if `ALPHAVANTAGE_API_KEY` is set
2. Yahoo Finance through `yfinance`
3. Local fallback CSV files already included in the repository

That means the script can still produce cleaned output even if an API is unavailable.

## Setup

```bash
python -m pip install -r requirements.txt
```

Optional: create a `.env` file from `.env.example` and add your Alpha Vantage API key.

## Run

```bash
python stock_pipeline.py
```

Cleaned files are written to:

- `stock_data/nse_nifty50_clean.csv`
- `stock_data/bse_sensex_clean.csv`

## Notes

- The notebook contains the original project workflow.
- The script is the easiest way to verify the project on a fresh machine.
- If `yfinance` fails because of environment-specific dependency issues, the script falls back to the included raw CSV files.
