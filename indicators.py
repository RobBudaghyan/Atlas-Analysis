# indicators.py

import pandas as pd
import ta
import logging
import math

class IndicatorCalculator:
    def __init__(self):
        pass

    def _get_trading_signals(self, latest, close_price):
        signals = {}
        if latest['rsi'] < 30:
            signals['RSI_Signal'] = 'Oversold'
        elif latest['rsi'] > 70:
            signals['RSI_Signal'] = 'Overbought'
        else:
            signals['RSI_Signal'] = 'Neutral'
        if latest['macd_hist'] > 0 and latest['macd_hist_prev'] < 0:
            signals['MACD_Signal'] = 'Bullish Crossover'
        elif latest['macd_hist'] > 0:
            signals['MACD_Signal'] = 'Bullish'
        elif latest['macd_hist'] < 0 and latest['macd_hist_prev'] > 0:
            signals['MACD_Signal'] = 'Bearish Crossover'
        else:
            signals['MACD_Signal'] = 'Bearish'
        if pd.notna(latest['sma_50']) and close_price > latest['sma_50']:
            signals['SMA_50_Signal'] = 'Above SMA50'
        else:
            signals['SMA_50_Signal'] = 'Below SMA50'
        if pd.notna(latest['sma_50']) and pd.notna(latest['sma_200']):
            is_cross_state = latest['sma_50'] > latest['sma_200']
            was_cross_state = latest['sma_50_prev'] > latest['sma_200_prev']
            if is_cross_state and not was_cross_state:
                signals['Cross_Signal'] = 'Golden Cross'
            elif not is_cross_state and was_cross_state:
                signals['Cross_Signal'] = 'Death Cross'
            else:
                signals['Cross_Signal'] = 'No Cross'
        else:
            signals['Cross_Signal'] = 'N/A'
        return signals

    def _get_trend_score(self, signals, latest, close_price):
        score = 0
        if pd.notna(latest['sma_200']) and close_price > latest['sma_200']:
            score += 3
        if signals.get('SMA_50_Signal') == 'Above SMA50':
            score += 1
        if signals.get('Cross_Signal') == 'Golden Cross':
            score += 2
        if pd.notna(latest['sma_200']) and close_price < latest['sma_200']:
            score -= 3
        if signals.get('Cross_Signal') == 'Death Cross':
            score -= 2
        return score

    def _get_momentum_score(self, signals, latest):
        score = 0
        if signals.get('MACD_Signal') == 'Bullish Crossover':
            score += 2
        elif signals.get('MACD_Signal') == 'Bullish':
            score += 1
        if latest['rsi'] > 55 and latest['rsi'] < 70:
            score += 1
        if signals.get('RSI_Signal') == 'Overbought':
            score -= 1
        if signals.get('RSI_Signal') == 'Oversold':
            score += 1
        if signals.get('MACD_Signal') == 'Bearish Crossover':
            score -= 2
        return score

    def calculate_indicators(self, df, timeframe_name):
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['sma_50_prev'] = df['sma_50'].shift(1)
        df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200)
        df['sma_200_prev'] = df['sma_200'].shift(1)
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        macd = ta.trend.MACD(df['close'])
        df['macd_hist'] = macd.macd_diff()
        df['macd_hist_prev'] = df['macd_hist'].shift(1)
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
        df['obv'] = ta.volume.on_balance_volume(df['close'], df['volume'])

        latest = df.iloc[-1]
        close_price = latest['close']

        signals = self._get_trading_signals(latest, close_price)
        trend_score = self._get_trend_score(signals, latest, close_price)
        momentum_score = self._get_momentum_score(signals, latest)

        max_trend_score = 6 if pd.notna(latest['sma_200']) else 1
        max_momentum_score = 4
        if max_trend_score == 0: max_trend_score = 1
        norm_trend_score = (trend_score / max_trend_score) * 10
        norm_momentum_score = (momentum_score / max_momentum_score) * 10
        final_score = (norm_trend_score * 0.60) + (norm_momentum_score * 0.40)

        results = {
            'Ticker': latest['ticker'],
            'Close_Price': "%.2f" % close_price,
            'RSI': "%.2f" % latest['rsi'] if pd.notna(latest['rsi']) else 'N/A',
            'MACD_Hist': "%.3f" % latest['macd_hist'] if pd.notna(latest['macd_hist']) else 'N/A',
            'ATR': "%.3f" % latest['atr'] if pd.notna(latest['atr']) else 'N/A',
            'OBV': int(latest['obv']) if pd.notna(latest['obv']) else 'N/A',
            'SMA_50': "%.2f" % latest['sma_50'] if pd.notna(latest['sma_50']) else 'N/A',
            'SMA_200': "%.2f" % latest['sma_200'] if pd.notna(latest['sma_200']) else 'N/A',
            'RSI_Signal': signals.get('RSI_Signal'),
            'MACD_Signal': signals.get('MACD_Signal'),
            'SMA_50_Signal': signals.get('SMA_50_Signal'),
            'Cross_Signal': signals.get('Cross_Signal'),
            'Trend_Score': trend_score,
            'Momentum_Score': momentum_score,
            'Final_Score': "%.2f" % final_score,
        }
        return results