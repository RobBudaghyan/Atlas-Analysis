# report_generator.py

import pandas as pd
import logging
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill


class ReportGenerator:
    def __init__(self):
        pass

    def _apply_conditional_formatting(self, worksheet, df):
        """Applies color formatting to signal and score cells."""
        bullish_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        bearish_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')

        bullish_terms = ['Bullish', 'Uptrend', 'Golden Cross', 'Oversold']
        bearish_terms = ['Bearish', 'Downtrend', 'Death Cross', 'Overbought']

        header_row = {cell.value: cell.column for cell in worksheet[1]}

        for col_name, col_idx in header_row.items():
            if 'Signal' in str(col_name):
                for row_idx, cell_value in enumerate(df[col_name], 2):
                    cell = worksheet.cell(row=row_idx, column=col_idx)
                    if any(term in str(cell_value) for term in bullish_terms):
                        cell.fill = bullish_fill
                    elif any(term in str(cell_value) for term in bearish_terms):
                        cell.fill = bearish_fill

            if 'Score' in str(col_name):
                for row_idx, cell_value in enumerate(df[col_name], 2):
                    if isinstance(cell_value, (int, float)):
                        cell = worksheet.cell(row=row_idx, column=col_idx)
                        if cell_value > 0:
                            cell.fill = bullish_fill
                        elif cell_value < 0:
                            cell.fill = bearish_fill

    # --- FIX: Added a 'filename' parameter to allow custom filenames ---
    def generate_report(self, all_results, master_rankings=None, filename='stock_analysis_report.xlsx'):
        logging.info(f"Generating report: {filename}...")

        # We check 'master_rankings' this way to avoid issues if an empty list is passed
        has_master_rankings = master_rankings is not None and len(master_rankings) > 0
        has_all_results = any(all_results.values())

        if not has_all_results and not has_master_rankings:
            logging.warning("No data was processed. The report will not be generated.")
            return

        writer = pd.ExcelWriter(filename, engine='openpyxl')

        if has_master_rankings:
            summary_df = pd.DataFrame(master_rankings)
            summary_df.set_index('Ticker', inplace=True)
            summary_df.to_excel(writer, sheet_name='Summary_Rankings')
            summary_worksheet = writer.sheets['Summary_Rankings']
            summary_df_for_formatting = summary_df.reset_index()
            self._apply_conditional_formatting(summary_worksheet, summary_df_for_formatting)
            logging.info("Created and formatted 'Summary_Rankings' sheet.")

        if has_all_results:
            for timeframe_name, results in all_results.items():
                if not results:
                    logging.warning(f"No results for timeframe {timeframe_name}. Skipping sheet.")
                    continue

                df = pd.DataFrame(results)
                df_for_formatting = df.copy()
                if 'Ticker' in df.columns:
                    df.set_index('Ticker', inplace=True)

                df.to_excel(writer, sheet_name=timeframe_name)
                worksheet = writer.sheets[timeframe_name]
                self._apply_conditional_formatting(worksheet, df_for_formatting)
                logging.info(f"Wrote and formatted sheet for {timeframe_name}.")

        writer.close()
        logging.info(f"Excel report saved as '{filename}'.")