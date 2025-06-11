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
            cache_path = os.path.join(DATA_CACHE_DIR, f"{ticker}_{timeframe_name}.csv")
            df = None

            if os.path.exists(cache_path):
                mod_time = os.path.getmtime(cache_path)
                if (time.time() - mod_time) / 3600 < 24:
                    try:
                        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                    except Exception as e:
                        logger.warning(f"Could not read cache for {ticker}. Refetching. Error: {e}")

            if df is None:
                try:
                    # Use group_by to handle cases where yfinance might return a MultiIndex even for one ticker
                    df = yf.download(
                        ticker,
                        period=params['period'],
                        interval=params['interval'],
                        auto_adjust=True,
                        progress=False,
                        group_by='ticker'
                    )
                    if not df.empty:
                        # If single ticker, yfinance might create a MultiIndex. Flatten it.
                        if len(ticker) > 0:
                            df.columns = df.columns.droplevel(0)
                        df.to_csv(cache_path)
                except Exception as e:
                    logger.error(f"Could not download data for {ticker}: {e}")
                    continue

            if df is None or df.empty:
                logger.warning(f"No data for {ticker}, skipping.")
                continue

            # Standardize all column names to lowercase
            df.columns = [col.lower() for col in df.columns]

            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"Data for {ticker} is missing required columns, skipping.")
                continue

            for col in required_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.dropna(subset=required_cols, inplace=True)

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
        master_rankings.append({
            'Ticker': ticker,
            'Master_Score': "%.2f" % master_score,
            'Long_Term_Score': "%.2f" % long_term_score,
            'Medium_Term_Score': "%.2f" % medium_term_score,
            'Short_Term_Score': "%.2f" % short_term_score
        })

    master_rankings = sorted(master_rankings, key=lambda x: float(x['Master_Score']), reverse=True)
    report_generator.generate_report(all_results, master_rankings)
    logger.info("Analysis complete. Program finished.")


if __name__ == "__main__":
    main()