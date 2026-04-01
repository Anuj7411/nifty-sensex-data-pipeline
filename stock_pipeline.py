import os
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from dotenv import load_dotenv


BASE_URL = "https://www.alphavantage.co/query"
OUTPUT_DIR = Path("stock_data")
PROXY_ENV_VARS = [
    "ALL_PROXY",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "all_proxy",
    "http_proxy",
    "https_proxy",
]


def _is_broken_loopback_proxy(value: str | None) -> bool:
    if not value:
        return False

    parsed = urlparse(value)
    hostname = (parsed.hostname or "").strip().lower()
    port = parsed.port
    return hostname in {"127.0.0.1", "localhost"} and port == 9


def disable_broken_proxy_settings() -> None:
    for key in PROXY_ENV_VARS:
        if _is_broken_loopback_proxy(os.environ.get(key)):
            os.environ.pop(key, None)


def fetch_alpha_vantage_data(symbol: str, api_key: str | None) -> pd.DataFrame | None:
    if not api_key:
        return None

    disable_broken_proxy_settings()

    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"Alpha Vantage request failed for {symbol}: {exc}")
        return None

    time_series = data.get("Time Series (Daily)")
    if not time_series:
        print(f"Alpha Vantage did not return daily data for {symbol}.")
        return None

    df = pd.DataFrame.from_dict(time_series, orient="index")
    df.rename(
        columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. adjusted close": "Adj Close",
            "6. volume": "Volume",
        },
        inplace=True,
    )
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def fetch_yfinance_data(symbol: str) -> pd.DataFrame | None:
    disable_broken_proxy_settings()

    try:
        import yfinance as yf
    except ImportError as exc:
        print(f"yfinance is unavailable: {exc}")
        return None

    try:
        df = yf.Ticker(symbol).history(period="max")
    except Exception as exc:
        print(f"Yahoo Finance request failed for {symbol}: {exc}")
        return None

    if df.empty:
        print(f"Yahoo Finance returned no data for {symbol}.")
        return None

    df.index.name = "Date"
    return df


def load_local_raw_csv(csv_path: Path) -> pd.DataFrame | None:
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    rename_map: dict[str, str] = {}
    for column in df.columns:
        lowered = column.lower()
        if lowered == "date":
            rename_map[column] = "Date"
        elif "open" in lowered:
            rename_map[column] = "Open"
        elif "high" in lowered:
            rename_map[column] = "High"
        elif "low" in lowered:
            rename_map[column] = "Low"
        elif "close" in lowered:
            rename_map[column] = "Close"
        elif "volume" in lowered:
            rename_map[column] = "Volume"

    df.rename(columns=rename_map, inplace=True)
    if "Date" not in df.columns:
        raise ValueError(f"Could not find a Date column in {csv_path}.")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)

    for column in ["Open", "High", "Low", "Close", "Volume"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def preprocess_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.dropna(how="all", inplace=True)
    cleaned.ffill(inplace=True)
    cleaned.index = pd.to_datetime(cleaned.index)
    cleaned.sort_index(inplace=True)

    columns = [col for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if col in cleaned.columns]
    return cleaned[columns]


def get_index_data(
    alpha_symbol: str,
    yahoo_symbol: str,
    local_csv_name: str,
    api_key: str | None,
) -> pd.DataFrame:
    data = fetch_alpha_vantage_data(alpha_symbol, api_key)
    if data is not None and not data.empty:
        print(f"Loaded {alpha_symbol} data from Alpha Vantage.")
        return data

    data = fetch_yfinance_data(yahoo_symbol)
    if data is not None and not data.empty:
        print(f"Loaded {yahoo_symbol} data from Yahoo Finance.")
        return data

    data = load_local_raw_csv(Path(local_csv_name))
    if data is not None and not data.empty:
        print(f"Loaded fallback data from local file {local_csv_name}.")
        return data

    raise RuntimeError(f"Unable to load data for {alpha_symbol}.")


def main() -> None:
    load_dotenv()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    nse_df = get_index_data("NSEI", "^NSEI", "nse.csv", api_key)
    bse_df = get_index_data("BSESN", "^BSESN", "bse.csv", api_key)

    nse_clean = preprocess_stock_data(nse_df)
    bse_clean = preprocess_stock_data(bse_df)

    OUTPUT_DIR.mkdir(exist_ok=True)
    nse_path = OUTPUT_DIR / "nse_nifty50_clean.csv"
    bse_path = OUTPUT_DIR / "bse_sensex_clean.csv"

    nse_clean.to_csv(nse_path)
    bse_clean.to_csv(bse_path)

    print(f"Saved NSE cleaned data to {nse_path}")
    print(f"Saved BSE cleaned data to {bse_path}")
    print("NSE shape:", nse_clean.shape)
    print("BSE shape:", bse_clean.shape)


if __name__ == "__main__":
    main()
