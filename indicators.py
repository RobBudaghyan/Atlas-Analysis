# indicators.py (Updated with Factor-Based Weighted Scoring)

import pandas as pd
import ta
import logging
import math


class IndicatorCalculator:
    def __init__(self):
        pass

    def _get_trading_signals(self, latest, close_price):
        """Generates simple text-based trading signals."""
        signals = {}
        # RSI Signal
        if latest['RSI'] < 30:
            signals['RSI_Signal'] = 'Oversold'
        elif latest['RSI'] > 70:
            signals['RSI_Signal'] = 'Overbought'
        else:
            signals['RSI_Signal'] = 'Neutral'
        # MACD Signal
        if latest['MACD_Hist'] > 0 and latest['MACD_Hist_Prev'] < 0:
            signals['MACD_Signal'] = 'Bullish Crossover'
        elif latest['MACD_Hist'] > 0:
            signals['MACD_Signal'] = 'Bullish'
        elif latest['MACD_Hist'] < 0 and latest['MACD_Hist_Prev'] > 0:
            signals['MACD_Signal'] = 'Bearish Crossover'
        else:
            signals['MACD_Signal'] = 'Bearish'
        # Moving Average Signal
        if pd.notna(latest['SMA_50']) and close_price > latest['SMA_50']:
            signals['SMA_50_Signal'] = 'Above SMA50'
        else:
            signals['SMA_50_Signal'] = 'Below SMA50'
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

    # --- NEW FACTOR-BASED SCORING ---

    def _get_trend_score(self, signals, latest, close_price):
        """Scores the quality and strength of the trend. Max score: 6"""
        score = 0
        if pd.notna(latest['SMA_200']) and close_price > latest['SMA_200']:
            score += 3  # Being above the 200-day average is the most important trend signal
        if signals.get('SMA_50_Signal') == 'Above SMA50':
            score += 1
        if signals.get('Cross_Signal') == 'Golden Cross':
            score += 2  # This is a powerful, but event-based signal
        # Penalize downtrends
        if pd.notna(latest['SMA_200']) and close_price < latest['SMA_200']:
            score -= 3
        if signals.get('Cross_Signal') == 'Death Cross':
            score -= 2
        return score

    def _get_momentum_score(self, signals, latest):
        """Scores the current momentum. Max score: 4"""
        score = 0
        if signals.get('MACD_Signal') == 'Bullish Crossover':
            score += 2  # A fresh crossover is a strong momentum signal
        elif signals.get('MACD_Signal') == 'Bullish':
            score += 1
        # Reward healthy RSI, penalize overbought
        if latest['RSI'] > 55 and latest['RSI'] < 70:
            score += 1  # Healthy bullish momentum
        if signals.get('RSI_Signal') == 'Overbought':
            score -= 1
        if signals.get('RSI_Signal') == 'Oversold':
            score += 1  # Oversold can be a bullish reversal signal in this context
        # Penalize bearish momentum
        if signals.get('MACD_Signal') == 'Bearish Crossover':
            score -= 2
        return score

    def calculate_indicators(self, df, timeframe_name):
        """
        Calculates all indicators and the new factor-based weighted score.
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

        # --- 3. Generate Signals and Factor Scores ---
        signals = self._get_trading_signals(latest, close_price)
        trend_score = self._get_trend_score(signals, latest, close_price)
        momentum_score = self._get_momentum_score(signals, latest)

        # --- 4. Calculate Final Weighted Score (out of 10) ---
        # Normalize factor scores to be on a 0-10 scale before applying weights
        # Max possible trend_score is 6, max momentum_score is 4
        # We handle cases where SMA200 is not available for short timeframes
        max_trend_score = 6 if pd.notna(latest['SMA_200']) else 1
        max_momentum_score = 4

        # Avoid division by zero if max_trend_score is somehow 0
        if max_trend_score == 0: max_trend_score = 1

        norm_trend_score = (trend_score / max_trend_score) * 10
        norm_momentum_score = (momentum_score / max_momentum_score) * 10

        # Apply weights
        final_score = (norm_trend_score * 0.60) + (norm_momentum_score * 0.40)

        # --- 5. Assemble results in the desired order ---
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
            'Trend_Score': trend_score,
            'Momentum_Score': momentum_score,
            'Final_Score': "%.2f" % final_score,
        }

        return results