# main.py

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
                    if ticker in df_batch.columns:
                        df = df_batch[ticker]
                        if df is None or not isinstance(df, pd.DataFrame): continue

                        df = df.copy().dropna(how='all')
                        if len(df) < 2: continue

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

    # --- CALCULATE MASTER SCORE AND RANKINGS ---
    logger.info("All timeframes analyzed. Calculating Master Score...")

    final_data = {}
    for timeframe_name, results_list in all_results.items():
        for result in results_list:
            ticker = result['Ticker']
            if ticker not in final_data:
                final_data[ticker] = {}
            # The 'Final_Score' is a string, convert it to a float for calculations
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

    # Pass both the detailed results and the new master rankings
    report_generator.generate_report(all_results, master_rankings)
    logger.info("Analysis complete. Program finished.")


if __name__ == "__main__":
    main()