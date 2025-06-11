# main.py

import yfinance as yf
import logging
import pandas as pd
from tqdm import tqdm
from indicators import IndicatorCalculator
from report_generator import ReportGenerator
import config
import time
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()

DATA_CACHE_DIR = 'data_cache'


def fetch_and_clean_data(ticker, timeframe_name, params):
    """
    Downloads data and robustly cleans it into a standard format.
    """
    cache_path = os.path.join(DATA_CACHE_DIR, f"{ticker}_{timeframe_name}.csv")

    if os.path.exists(cache_path):
        mod_time = os.path.getmtime(cache_path)
        if (time.time() - mod_time) / 3600 < 24:
            try:
                return pd.read_csv(cache_path, index_col=0, parse_dates=True)
            except Exception as e:
                logger.warning(f"Cache file for {ticker} is corrupt. Refetching. Error: {e}")

    try:
        raw_df = yf.download(
            ticker, period=params['period'], interval=params['interval'],
            auto_adjust=True, progress=False
        )
        if raw_df is None or raw_df.empty:
            return None

        clean_df = pd.DataFrame(index=raw_df.index)

        for col in raw_df.columns:
            col_name_str = str(col).lower()
            if 'open' in col_name_str:
                clean_df['open'] = raw_df[col]
            elif 'high' in col_name_str:
                clean_df['high'] = raw_df[col]
            elif 'low' in col_name_str:
                clean_df['low'] = raw_df[col]
            elif 'close' in col_name_str:
                clean_df['close'] = raw_df[col]
            elif 'volume' in col_name_str:
                clean_df['volume'] = raw_df[col]

        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in clean_df.columns for col in required_cols):
            logger.warning(f"Could not find all required columns for {ticker}. Found: {list(clean_df.columns)}")
            return None

        clean_df.to_csv(cache_path)
        return clean_df

    except Exception as e:
        logger.error(f"Failed to download or process data for {ticker}: {e}")
        return None


def main():
    os.makedirs(DATA_CACHE_DIR, exist_ok=True)
    indicator_calculator = IndicatorCalculator()
    report_generator = ReportGenerator()
    all_results = {}

    logger.info(f"Starting analysis for {len(config.TICKERS)} tickers...")

    for timeframe_name, params in config.TIMEFRAMES.items():
        logger.info(f"Processing timeframe: {timeframe_name}...")
        timeframe_results = []

        for ticker in tqdm(config.TICKERS, desc=f"Analyzing {timeframe_name}", unit="ticker"):
            df = fetch_and_clean_data(ticker, timeframe_name, params)

            if df is None:
                continue

            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(inplace=True)

            if len(df) < 50:
                logger.warning(f"Not enough valid data for {ticker} after cleaning, skipping.")
                continue

            df['ticker'] = ticker
            indicators = indicator_calculator.calculate_indicators(df.copy(), timeframe_name)
            if indicators:
                timeframe_results.append(indicators)

        all_results[timeframe_name] = timeframe_results

    logger.info("All timeframes analyzed. Calculating Master Score...")
    final_data = {}
    for timeframe_name, results_list in all_results.items():
        for result in results_list:
            ticker = result['Ticker']
            if ticker not in final_data:
                final_data[ticker] = {}
            final_data[ticker][f"{timeframe_name}_Score"] = float(result.get('Final_Score', 0.0))

    master_rankings = []
    for ticker, scores in final_data.items():
        long_term_score = scores.get('Long_Term_Analysis_Score', 0.0)
        medium_term_score = scores.get('Medium_Term_Analysis_Score', 0.0)
        short_term_score = scores.get('Short_Term_Analysis_Score', 0.0)
        master_score = (long_term_score * 0.5) + (medium_term_score * 0.3) + (short_term_score * 0.2)

        # --- FIX: Reorder the columns as requested ---
        master_rankings.append({
            'Ticker': ticker,
            'Short_Term_Score': "%.2f" % short_term_score,
            'Medium_Term_Score': "%.2f" % medium_term_score,
            'Long_Term_Score': "%.2f" % long_term_score,
            'Master_Score': "%.2f" % master_score
        })

    master_rankings = sorted(master_rankings, key=lambda x: float(x['Master_Score']), reverse=True)

    report_generator.generate_report(all_results, master_rankings)
    logger.info("Analysis complete. Program finished.")


if __name__ == "__main__":
    main()