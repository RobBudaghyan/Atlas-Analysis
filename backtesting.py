# backtester.py (Corrected and Final Version)

import yfinance as yf
import logging
import pandas as pd
from tqdm import tqdm
import time
from datetime import datetime, timedelta

# Import the classes from our existing project files
from indicators import IndicatorCalculator
from report_generator import ReportGenerator
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()

# --- Backtesting Configuration ---
BACKTEST_END_DATE = '2024-01-01'
OUTPUT_FILENAME = f"backtest_report_{BACKTEST_END_DATE}.xlsx"


def run_historical_analysis():
    """
    Runs the same analysis as main.py, but for a specific historical date.
    """
    indicator_calculator = IndicatorCalculator()
    report_generator = ReportGenerator()
    all_results = {}

    logger.info(f"--- Starting Backtest Analysis for date: {BACKTEST_END_DATE} ---")
    logger.info(f"Analyzing {len(config.TICKERS)} tickers...")

    for timeframe_name, params in config.TIMEFRAMES.items():
        logger.info(f"Processing timeframe: {timeframe_name}...")

        timeframe_results = []
        chunk_size = 50
        ticker_chunks = [config.TICKERS[i:i + chunk_size] for i in range(0, len(config.TICKERS), chunk_size)]

        logger.info(f"Splitting tickers into {len(ticker_chunks)} chunks of {chunk_size}.")

        end_date_dt = datetime.strptime(BACKTEST_END_DATE, '%Y-%m-%d')
        period_str = params['period']
        # Calculate start date to ensure enough data for indicators
        if 'y' in period_str:
            years = int(period_str.replace('y', ''))
            start_date_dt = end_date_dt - timedelta(days=years * 365 + 90)
        elif 'mo' in period_str:
            months = int(period_str.replace('mo', ''))
            start_date_dt = end_date_dt - timedelta(days=months * 31 + 90)
        else:
            start_date_dt = end_date_dt - timedelta(days=5 * 365)
        start_date_str = start_date_dt.strftime('%Y-%m-%d')

        for i, chunk in enumerate(ticker_chunks):
            logger.info(f"Processing chunk {i + 1}/{len(ticker_chunks)}...")
            try:
                df_batch = yf.download(
                    chunk,
                    start=start_date_str,
                    end=BACKTEST_END_DATE,
                    interval=params['interval'],
                    group_by='ticker',
                    auto_adjust=True,
                    progress=False
                )

                if df_batch.empty:
                    logger.warning(f"No data loaded for chunk {i + 1}.")
                    continue

                for ticker in tqdm(chunk, desc=f"Analyzing chunk {i + 1}", unit="ticker"):
                    if ticker in df_batch.columns:
                        df = df_batch[ticker]
                        if df is None or not isinstance(df, pd.DataFrame):
                            continue

                        df = df.copy().dropna(how='all')

                        # --- FIX 1: Removed the overly strict data check ---
                        # The check 'len(df) < 200' was removed. The 'len(df) < 2' check is sufficient.
                        # The indicator calculator is already robust enough to handle missing SMA200 values.
                        if len(df) < 2:
                            continue

                        df['Ticker'] = ticker
                        indicators = indicator_calculator.calculate_indicators(df, timeframe_name)

                        if indicators:
                            timeframe_results.append(indicators)

                logger.info("Chunk complete. Pausing for 3 seconds...")
                time.sleep(3)

            except Exception as e:
                logger.error(f"A critical error occurred processing chunk {i + 1}: {e}")
                continue

        all_results[timeframe_name] = timeframe_results

    # --- FIX 2: Added the Master Score calculation logic back in ---
    logger.info("All timeframes analyzed. Calculating Master Score for backtest...")

    final_data = {}
    for timeframe_name, results_list in all_results.items():
        for result in results_list:
            ticker = result['Ticker']
            if ticker not in final_data: final_data[ticker] = {}
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

    # Pass all data to the report generator to create all sheets
    report_generator.generate_report(all_results, master_rankings=master_rankings, filename=OUTPUT_FILENAME)
    logger.info("Backtest analysis complete.")


if __name__ == "__main__":
    run_historical_analysis()