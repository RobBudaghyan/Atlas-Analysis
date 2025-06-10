# main.py (Final Robust Version)

import yfinance as yf
import logging
import pandas as pd
from tqdm import tqdm
from indicators import IndicatorCalculator
from report_generator import ReportGenerator
import config
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger()


def main():
    indicator_calculator = IndicatorCalculator()
    report_generator = ReportGenerator()
    all_results = {}

    logger.info(f"Starting analysis for {len(config.TICKERS)} tickers...")

    for timeframe_name, params in config.TIMEFRAMES.items():
        logger.info(f"Processing timeframe: {timeframe_name}...")

        timeframe_results = []
        chunk_size = 50
        ticker_chunks = [config.TICKERS[i:i + chunk_size] for i in range(0, len(config.TICKERS), chunk_size)]

        logger.info(f"Splitting {len(config.TICKERS)} tickers into {len(ticker_chunks)} chunks of {chunk_size}.")

        for i, chunk in enumerate(ticker_chunks):
            logger.info(f"Processing chunk {i + 1}/{len(ticker_chunks)}...")
            try:
                df_batch = yf.download(
                    chunk,
                    period=params['period'],
                    interval=params['interval'],
                    group_by='ticker',
                    auto_adjust=True,
                    progress=False
                )

                if df_batch.empty:
                    logger.warning(f"No data loaded for chunk {i + 1}.")
                    continue

                for ticker in tqdm(chunk, desc=f"Analyzing chunk {i + 1}", unit="ticker"):
                    # Check if the ticker exists in the downloaded columns
                    if ticker in df_batch.columns:
                        df = df_batch[ticker]  # Access data directly

                        # --- FIX 1: ADDED 'None' and DATAFRAME CHECK ---
                        # yfinance can return None for a failed ticker in a batch
                        if df is None or not isinstance(df, pd.DataFrame):
                            continue

                        df = df.copy().dropna(how='all')

                        if len(df) < 2:
                            continue

                        df['Ticker'] = ticker
                        indicators = indicator_calculator.calculate_indicators(df, timeframe_name)

                        if indicators:
                            timeframe_results.append(indicators)

                # --- FIX 2: INCREASED PAUSE DURATION ---
                logger.info("Chunk complete. Pausing for 2 seconds...")
                time.sleep(2)

            except Exception as e:
                logger.error(f"A critical error occurred processing chunk {i + 1}: {e}")
                continue

        all_results[timeframe_name] = timeframe_results

    report_generator.generate_report(all_results)
    logger.info("Analysis complete. Program finished.")


if __name__ == "__main__":
    main()