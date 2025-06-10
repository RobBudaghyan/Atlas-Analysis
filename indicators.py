# indicators.py

import pandas as pd
import ta
import logging


class IndicatorCalculator:
    def __init__(self):
        pass

    def _get_trading_signals(self, latest, close_price):
        """Generates simple trading signals based on indicator values."""
        signals = {}

        # RSI Signal
        if latest['RSI'] < 30:
            signals['RSI_Signal'] = 'Bullish (Oversold)'
        elif latest['RSI'] > 70:
            signals['RSI_Signal'] = 'Bearish (Overbought)'
        else:
            signals['RSI_Signal'] = 'Neutral'

        # MACD Signal
        if latest['MACD_Hist'] > 0:
            signals['MACD_Signal'] = 'Bullish'
        else:
            signals['MACD_Signal'] = 'Bearish'

        # Moving Average Signal (Price vs 50-day SMA)
        if close_price > latest['SMA_50']:
            signals['SMA_50_Signal'] = 'Bullish (Above MA)'
        else:
            signals['SMA_50_Signal'] = 'Bearish (Below MA)'

        # Golden/Death Cross Signal (50-day SMA vs 200-day SMA)
        if pd.notna(latest['SMA_50']) and pd.notna(latest['SMA_200']):
            if latest['SMA_50'] > latest['SMA_200']:
                signals['Cross_Signal'] = 'Golden Cross (Bullish)'
            else:
                signals['Cross_Signal'] = 'Death Cross (Bearish)'
        else:
            signals['Cross_Signal'] = 'N/A'

        return signals

    def calculate_indicators(self, df, timeframe):
        results = {}

        # --- 1. Add all technical indicators ---
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['EMA_20'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['EMA_50'] = ta.trend.ema_indicator(df['Close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        macd = ta.trend.MACD(df['Close'])
        df['MACD_Hist'] = macd.macd_diff()
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])

        latest = df.iloc[-1]
        close_price = latest['Close']

        if pd.isna(close_price) or close_price == 0:
            logging.warning(f"Invalid close price for {df['Ticker'].iloc[0]}. Skipping.")
            return {}

        # --- 2. Compile the indicator values ---
        results['Ticker'] = latest['Ticker']
        results['Close_Price'] = close_price
        results['RSI'] = latest['RSI'] if pd.notna(latest['RSI']) else 50.0
        results['MACD_Hist'] = latest['MACD_Hist'] if pd.notna(latest['MACD_Hist']) else 0.0
        results['ATR'] = latest['ATR'] if pd.notna(latest['ATR']) else 0.0
        results['OBV'] = latest['OBV'] if pd.notna(latest['OBV']) else 0
        results['SMA_50'] = latest['SMA_50'] if pd.notna(latest['SMA_50']) else 0.0
        results['SMA_200'] = latest['SMA_200'] if pd.notna(latest['SMA_200']) else 0.0

        # --- 3. Generate and add trading signals ---
        signals = self._get_trading_signals(latest, close_price)
        results.update(signals)

        logging.debug(f"Processed indicators for {results['Ticker']}: {results}")

        return results