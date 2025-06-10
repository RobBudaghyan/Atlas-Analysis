# indicators.py

import pandas as pd
import ta
import logging


class IndicatorCalculator:
    def __init__(self):
        pass

    def _calculate_pct_diff(self, value1, value2):
        """Helper function to calculate the percentage difference."""
        if pd.isna(value1) or pd.isna(value2) or value2 == 0:
            return 0.0
        return ((value1 - value2) / abs(value2)) * 100

    def calculate_indicators(self, df, timeframe):
        """
        Calculates technical indicators and returns them as numerical values.
        """
        results = {}

        # --- 1. Add all technical indicators to the DataFrame ---
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

        # MACD calculation
        macd = ta.trend.MACD(df['Close'])
        df['MACD_Hist'] = macd.macd_diff()  # MACD Histogram (MACD Line - Signal Line)

        # Volatility and Volume
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        df['BB_High'] = ta.volatility.bollinger_hband(df['Close'], window=20)
        df['BB_Low'] = ta.volatility.bollinger_lband(df['Close'], window=20)
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])

        # --- 2. Get the most recent indicator values ---
        latest = df.iloc[-1]
        close_price = latest['Close']

        if pd.isna(close_price) or close_price == 0:
            logging.warning(f"Invalid close price for {df['Ticker'].iloc[0]}. Skipping analysis.")
            return {}

        # --- 3. Compile the results with numerical scores ---
        results['Ticker'] = latest['Ticker']

        # Trend Indicators: Price's % difference from the moving average
        results['SMA_50_Pct_Diff'] = self._calculate_pct_diff(close_price, latest['SMA_50'])
        results['SMA_200_Pct_Diff'] = self._calculate_pct_diff(close_price, latest['SMA_200'])
        results['EMA_20_Pct_Diff'] = self._calculate_pct_diff(close_price, latest['EMA_20'])
        results['EMA_50_Pct_Diff'] = self._calculate_pct_diff(close_price, latest['EMA_50'])

        # RSI: The raw RSI score (0-100)
        results['RSI'] = latest['RSI'] if pd.notna(latest['RSI']) else 50.0

        # MACD: Histogram value as a percentage of the closing price
        results['MACD_Hist_Pct'] = self._calculate_pct_diff(latest['MACD_Hist'], close_price)

        # Volatility: ATR and BB Width as a percentage of price
        results['ATR_Pct'] = self._calculate_pct_diff(latest['ATR'], close_price)
        bb_width = latest['BB_High'] - latest['BB_Low']
        results['BB_Width_Pct'] = self._calculate_pct_diff(bb_width, close_price)

        # OBV: Raw value (cumulative, not suitable for percentage difference)
        results['OBV'] = latest['OBV'] if pd.notna(latest['OBV']) else 0

        logging.debug(f"Processed indicators for {results['Ticker']}: {results}")

        return results