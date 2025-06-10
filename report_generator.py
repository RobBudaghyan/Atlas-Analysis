# report_generator.py

import pandas as pd
import logging
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill

class ReportGenerator:
    def __init__(self):
        pass

    def _apply_conditional_formatting(self, worksheet, df):
        """Applies color formatting to signal cells."""
        bullish_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        bearish_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

        header_row = {cell.value: cell.column for cell in worksheet[1]}

        for col_name, col_idx in header_row.items():
            if 'Signal' in str(col_name):
                for row_idx, cell_value in enumerate(df[col_name], 2):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    if 'Bullish' in str(cell_value):
                        cell.fill = bullish_fill
                    elif 'Bearish' in str(cell_value):
                        cell.fill = bearish_fill

    def generate_report(self, all_results):
        logging.info("Generating data-only Excel report...")

        if not any(all_results.values()):
            logging.warning("No data was processed for any timeframe. The report will not be generated.")
            return

        writer = pd.ExcelWriter('stock_analysis_report.xlsx', engine='openpyxl')

        for timeframe_name, results in all_results.items():
            if not results:
                logging.warning(f"No results for timeframe {timeframe_name}. Skipping sheet.")
                continue

            df = pd.DataFrame(results)
            if 'Ticker' in df.columns:
                df.set_index('Ticker', inplace=True)

            df.to_excel(writer, sheet_name=timeframe_name)
            worksheet = writer.sheets[timeframe_name]
            self._apply_conditional_formatting(worksheet, df)

            logging.info(f"Wrote and formatted sheet for {timeframe_name}.")

        writer.close()
        logging.info("Excel report saved as 'stock_analysis_report.xlsx'.")