# Nifty Sensex Data Pipeline

An end-to-end data pipeline for collecting, cleaning, and exporting historical market index data for India's two most tracked benchmarks:

- Nifty 50
- BSE Sensex

Built as a practical data engineering and market analytics project, this repository combines API-based fetching, fallback handling, preprocessing, and export-ready CSV generation in one simple workflow.

## Why This Project Stands Out

- Pulls historical market data for major Indian indices
- Supports multiple data sources for better reliability
- Cleans and standardizes raw market data into analysis-ready datasets
- Includes both a notebook workflow and a script-based pipeline
- Handles real-world environment issues like broken proxy settings and provider failures

## Data Flow

The pipeline fetches index data in the following order:

1. Alpha Vantage, if `ALPHAVANTAGE_API_KEY` is available
2. Yahoo Finance through `yfinance`
3. Local fallback CSV files bundled with the project

This makes the project more resilient than a single-source scraper and helps it keep working even when one data provider is unavailable.

## Project Structure

```text
.
|-- Stock_market.ipynb
|-- stock_pipeline.py
|-- requirements.txt
|-- .env.example
|-- nse.csv
|-- bse.csv
`-- stock_data/
    |-- nse_nifty50_clean.csv
    `-- bse_sensex_clean.csv
```

## Tech Stack

- Python
- Pandas
- Requests
- yfinance
- python-dotenv
- Jupyter Notebook

## Quick Start

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Optional: create a `.env` file from `.env.example` and add your Alpha Vantage API key.

```env
ALPHAVANTAGE_API_KEY=your_api_key_here
```

Run the pipeline:

```bash
python stock_pipeline.py
```

## Output

The script generates cleaned CSV files inside `stock_data/`:

- `stock_data/nse_nifty50_clean.csv`
- `stock_data/bse_sensex_clean.csv`

These files are structured for further:

- data analysis
- visualization
- machine learning workflows
- trend and market behavior studies

## What The Pipeline Cleans

- standardizes date handling
- converts numeric columns into proper numeric types
- removes empty rows
- forward-fills missing values when needed
- keeps only the core market columns: `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`

## Notebook + Script Workflow

This repository includes two ways to explore the project:

- `Stock_market.ipynb` for the original notebook-based workflow
- `stock_pipeline.py` for a reproducible script-based run

The script version is the best option for validating the project on a fresh machine or using it as a portfolio-ready repository.

## Reliability Notes

- If Alpha Vantage is unavailable, the pipeline automatically tries Yahoo Finance.
- If Yahoo Finance also fails, the project falls back to the included raw CSV files.
- The script also guards against broken loopback proxy settings that can block network fetches on some local environments.

## Use Cases

- beginner-friendly data engineering portfolio project
- stock market data collection workflow
- preprocessing pipeline for financial datasets
- foundation for forecasting or price trend analysis
- starting point for dashboard or visualization projects

## Future Improvements

- add scheduled automatic data refresh
- add technical indicators like RSI, MACD, and moving averages
- build dashboards with Streamlit or Power BI
- export charts and summary analytics
- add unit tests for the data cleaning functions

## License

This project is licensed under the MIT License.
