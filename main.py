# main.py

import yfinance as yf
import logging
import pandas as pd
from tqdm import tqdm
import ta  # Technical Analysis library
from indicators import IndicatorCalculator
from report_generator import ReportGenerator
import config
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()


def main():
    indicator_calculator = IndicatorCalculator()
    report_generator = ReportGenerator()
    all_results = {}

    logger.info(f"Starting analysis for tickers: {config.TICKERS}")

    for timeframe_name, params in config.TIMEFRAMES.items():
        logger.info(f"Processing timeframe: {timeframe_name} with params {params}")

        timeframe_results = []

        try:
            logger.info(f"Attempting to load data for all tickers ({timeframe_name})...")

            # Download all ticker data in one batch
            # Added auto_adjust=True to fix the FutureWarning
            df_batch = yf.download(
                config.TICKERS,
                period=params['period'],
                interval=params['interval'],
                group_by='ticker',
                auto_adjust=True
            )

            if df_batch.empty or df_batch.columns.nlevels == 0:
                logger.warning(f"No data was loaded for any tickers in {timeframe_name}.")
                continue

            for ticker in tqdm(config.TICKERS, desc=f"{timeframe_name} progress", unit="ticker"):
                if ticker in df_batch.columns:
                    df = df_batch[ticker].copy()
                    df.dropna(how='all', inplace=True)

                    if df.empty:
                        continue

                    df['Ticker'] = ticker

                    # Calculate indicators for the report
                    indicators = indicator_calculator.calculate_indicators(df, timeframe_name)
                    if indicators:
                        timeframe_results.append(indicators)

        except Exception as e:
            logger.error(f"A critical error occurred during the {timeframe_name} processing: {e}")
            continue

        all_results[timeframe_name] = timeframe_results

    # Pass only the results to the report generator
    report_generator.generate_report(all_results)
    logger.info("Analysis complete. Program finished.")


if __name__ == "__main__":
    main()