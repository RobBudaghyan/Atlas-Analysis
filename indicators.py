# indicators.py

import pandas as pd
import ta
import logging


class IndicatorCalculator:
    def __init__(self):
        pass

    def _get_trading_signals(self, latest, close_price):
        """Generates simple text-based trading signals."""
        signals = {}

        # RSI Signal
        if latest['RSI'] < 30:
            signals['RSI_Signal'] = 'Bullish'
        elif latest['RSI'] > 70:
            signals['RSI_Signal'] = 'Bearish'
        else:
            signals['RSI_Signal'] = 'Neutral'

        # MACD Signal
        if latest['MACD_Hist'] > 0 and latest['MACD_Hist_Prev'] < 0:
            signals['MACD_Signal'] = 'Bullish Crossover'
        elif latest['MACD_Hist'] > 0:
            signals['MACD_Signal'] = 'Bullish'
        elif latest['MACD_Hist'] < 0 and latest['MACD_Hist_Prev'] > 0:
            signals['MACD_Signal'] = 'Bearish Crossover'
        else:  # MACD_Hist < 0
            signals['MACD_Signal'] = 'Bearish'

        # Moving Average Signal
        if pd.notna(latest['SMA_50']) and close_price > latest['SMA_50']:
            signals['SMA_50_Signal'] = 'Uptrend'
        else:
            signals['SMA_50_Signal'] = 'Downtrend'

        # Golden/Death Cross Signal
        if pd.notna(latest['SMA_50']) and pd.notna(latest['SMA_200']):
            is_cross_state = latest['SMA_50'] > latest['SMA_200']
            was_cross_state = latest['SMA_50_Prev'] > latest['SMA_200_Prev']
            if is_cross_state and not was_cross_state:
                signals['Cross_Signal'] = 'Golden Cross'
            elif not is_cross_state and was_cross_state:
                signals['Cross_Signal'] = 'Death Cross'
            else:
                signals['Cross_Signal'] = 'No Cross'
        else:
            signals['Cross_Signal'] = 'N/A'

        return signals

    def _get_technical_score(self, signals):
        """
        Generates a balanced score by adding points for bullish signals
        and subtracting points for bearish signals.
        """
        score = 0

        # --- Bullish Signals (Add Points) ---
        if signals.get('RSI_Signal') == 'Bullish': score += 2
        if signals.get('MACD_Signal') == 'Bullish Crossover':
            score += 2
        elif signals.get('MACD_Signal') == 'Bullish':
            score += 1
        if signals.get('SMA_50_Signal') == 'Uptrend': score += 1
        if signals.get('Cross_Signal') == 'Golden Cross': score += 3

        # --- Bearish Signals (Subtract Points) ---
        if signals.get('RSI_Signal') == 'Bearish': score -= 2
        if signals.get('MACD_Signal') == 'Bearish Crossover':
            score -= 2
        elif signals.get('MACD_Signal') == 'Bearish':
            score -= 1
        if signals.get('SMA_50_Signal') == 'Downtrend': score -= 1
        if signals.get('Cross_Signal') == 'Death Cross': score -= 3

        return score

    def calculate_indicators(self, df, timeframe_name):
        """
        Calculates all indicators and returns them in the user-specified order.
        """
        # --- 1. Calculate All Technical Indicators ---
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_50_Prev'] = df['SMA_50'].shift(1)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['SMA_200_Prev'] = df['SMA_200'].shift(1)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        macd = ta.trend.MACD(df['Close'])
        df['MACD_Hist'] = macd.macd_diff()
        df['MACD_Hist_Prev'] = df['MACD_Hist'].shift(1)
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'], window=14)
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])

        # --- 2. Get latest data ---
        latest = df.iloc[-1]
        close_price = latest['Close']
        if pd.isna(close_price): return {}

        # --- 3. Generate Signals and Score ---
        signals = self._get_trading_signals(latest, close_price)
        technical_score = self._get_technical_score(signals)

        # --- 4. Assemble results in the desired order ---
        results = {
            'Ticker': latest['Ticker'],
            'Close_Price': "%.2f" % close_price,
            'RSI': "%.2f" % latest['RSI'] if pd.notna(latest['RSI']) else 'N/A',
            'MACD_Hist': "%.3f" % latest['MACD_Hist'] if pd.notna(latest['MACD_Hist']) else 'N/A',
            'ATR': "%.3f" % latest['ATR'] if pd.notna(latest['ATR']) else 'N/A',
            'OBV': int(latest['OBV']) if pd.notna(latest['OBV']) else 'N/A',
            'SMA_50': "%.2f" % latest['SMA_50'] if pd.notna(latest['SMA_50']) else 'N/A',
            'SMA_200': "%.2f" % latest['SMA_200'] if pd.notna(latest['SMA_200']) else 'N/A',
            'RSI_Signal': signals.get('RSI_Signal'),
            'MACD_Signal': signals.get('MACD_Signal'),
            'SMA_50_Signal': signals.get('SMA_50_Signal'),
            'Cross_Signal': signals.get('Cross_Signal'),
            'Score': technical_score,  # Renamed from "Bullish_Score"
        }

        return results