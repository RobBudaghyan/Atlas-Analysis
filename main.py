# main.py

import yfinance as yf
import logging
import pandas as pd
from tqdm import tqdm
from indicators import IndicatorCalculator
from report_generator import ReportGenerator
import config

# Simple logging (no colors)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

logger = logging.getLogger()

def main():
    indicator_calculator = IndicatorCalculator()
    report_generator = ReportGenerator()
    all_results = {}

    logger.info(f"Starting analysis for tickers: {config.TICKERS}")

    for timeframe_name, params in config.TIMEFRAMES.items():
        logger.info(f"Processing timeframe: {timeframe_name} with params {params}")

        timeframe_results = []

        for ticker in tqdm(config.TICKERS, desc=f"{timeframe_name} progress", unit="ticker"):

            try:
                logger.info(f"Loading data for {ticker} ({timeframe_name})")
                df = yf.download(ticker, period=params['period'], interval=params['interval'])

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df['Ticker'] = ticker

                logger.info(f"Calculating indicators for {ticker} ({timeframe_name})")
                indicators = indicator_calculator.calculate_indicators(df, timeframe_name)

                timeframe_results.append(indicators)

            except Exception as e:
                logger.error(f"Error processing {ticker} in {timeframe_name}: {e}")

        all_results[timeframe_name] = timeframe_results

    report_generator.generate_report(all_results)
    logger.info("Analysis complete. Program finished.")

if __name__ == "__main__":
    main()
