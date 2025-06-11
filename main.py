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
TIME_SLEEP = 0


def process_and_analyze_ticker(df, ticker, timeframe_name, indicator_calculator):
    """
    Cleans a single ticker's DataFrame and runs the indicator analysis.
    This function is called after data is either loaded from cache or downloaded.
    """
    if df is None or df.empty:
        return None

    try:
        # Clean the data
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)

        if len(df) < 50:
            logger.warning(f"Not enough valid data for {ticker} after cleaning, skipping.")
            return None

        # Run analysis
        df['ticker'] = ticker
        indicators = indicator_calculator.calculate_indicators(df.copy(), timeframe_name)
        return indicators
    except Exception as e:
        logger.error(f"Error processing data for {ticker}: {e}")
        return None


def main():
    os.makedirs(DATA_CACHE_DIR, exist_ok=True)
    indicator_calculator = IndicatorCalculator()
    report_generator = ReportGenerator()
    all_results = {}

    logger.info(f"Starting analysis for {len(config.TICKERS)} tickers...")

    # --- CHUNKING LOGIC ---
    chunk_size = 100  # Process 100 tickers at a time
    ticker_chunks = [config.TICKERS[i:i + chunk_size] for i in range(0, len(config.TICKERS), chunk_size)]

    for timeframe_name, params in config.TIMEFRAMES.items():
        logger.info(f"Processing timeframe: {timeframe_name}...")
        timeframe_results = []

        progress_bar = tqdm(total=len(config.TICKERS), desc=f"Analyzing {timeframe_name}")

        for i, chunk in enumerate(ticker_chunks):
            logger.info(f"Processing chunk {i + 1}/{len(ticker_chunks)} ({len(chunk)} tickers)")

            tickers_to_download = []

            # First, process any tickers in the chunk that are already in the cache
            for ticker in chunk:
                cache_path = os.path.join(DATA_CACHE_DIR, f"{ticker}_{timeframe_name}.csv")
                if os.path.exists(cache_path):
                    try:
                        mod_time = os.path.getmtime(cache_path)
                        if (time.time() - mod_time) / 3600 < 24:  # Check if cache is fresh
                            df_cached = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                            indicators = process_and_analyze_ticker(df_cached, ticker, timeframe_name,
                                                                    indicator_calculator)
                            if indicators:
                                timeframe_results.append(indicators)
                            progress_bar.update(1)
                        else:  # Cache is stale, needs re-downloading
                            tickers_to_download.append(ticker)
                    except Exception as e:
                        logger.warning(f"Cache file for {ticker} corrupt. Refetching. Error: {e}")
                        tickers_to_download.append(ticker)
                else:  # No cache file exists
                    tickers_to_download.append(ticker)

            # Now, download the batch of tickers that weren't in the cache
            if tickers_to_download:
                try:
                    data_batch = yf.download(
                        tickers_to_download,
                        period=params['period'],
                        interval=params['interval'],
                        auto_adjust=True,
                        progress=False,
                        group_by='ticker'
                    )

                    # Process and cache each ticker from the newly downloaded batch
                    for ticker in tickers_to_download:
                        df_ticker = None
                        if not data_batch.empty and ticker in data_batch.columns.get_level_values(0):
                            df_ticker = data_batch.loc[:, ticker].copy()
                            df_ticker.columns = [str(col).lower() for col in df_ticker.columns]

                            # Save the clean data to cache
                            cache_path = os.path.join(DATA_CACHE_DIR, f"{ticker}_{timeframe_name}.csv")
                            df_ticker.to_csv(cache_path)

                        indicators = process_and_analyze_ticker(df_ticker, ticker, timeframe_name, indicator_calculator)
                        if indicators:
                            timeframe_results.append(indicators)

                        progress_bar.update(1)

                except Exception as e:
                    logger.error(f"An error occurred downloading chunk {i + 1}: {e}")
                    progress_bar.update(len(tickers_to_download))

            # Pause for 10 seconds between each chunk
            logger.info(f"Chunk {i + 1} complete. Pausing for 10 seconds...")
            time.sleep(TIME_SLEEP)

        progress_bar.close()
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
