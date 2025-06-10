# report_generator.py

import pandas as pd
import logging

class ReportGenerator:
    def __init__(self):
        pass

    def generate_report(self, all_results):
        logging.info("Generating Excel report...")
        writer = pd.ExcelWriter('stock_analysis_report.xlsx', engine='openpyxl')

        sheets_written = 0

        for timeframe_name, results in all_results.items():
            if not results:
                logging.warning(f"No results for timeframe {timeframe_name}. Skipping sheet.")
                continue

            df = pd.DataFrame(results)

            if 'Ticker' in df.columns:
                df.set_index('Ticker', inplace=True)

            df.to_excel(writer, sheet_name=timeframe_name)
            logging.info(f"Wrote sheet for {timeframe_name}.")
            sheets_written += 1

        if sheets_written == 0:
            logging.warning("No sheets were generated. Excel file will not be saved.")
            writer.close()
            return

        writer.close()
        logging.info("Excel report saved as 'stock_analysis_report.xlsx'.")
