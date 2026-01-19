                                                                                                                                                                                                                                                                                            """
Stock Analysis Engine
Provides comprehensive stock analysis with probability-based trend assessment
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from technical_indicators import TechnicalIndicators
from risk_manager import RiskManager


class StockAnalyzer:
    """Analyze stocks and generate trading recommendations"""

    MARKET_SESSIONS = {
        'pre_open': (9, 15),      
        'opening': (9, 16, 10, 30),  
        'mid_session': (10, 31, 14, 30),  
        'closing': (14, 31, 15, 30),  
        'post_close': (15, 31, 16, 0)  
    }

    STOCK_CAPS = {
        'large_cap': (50000, float('inf')),      
        'mid_cap': (5000, 50000),                
        'small_cap': (500, 5000),                
        'micro_cap': (0, 500)                    
    }

    @staticmethod
    def get_stock_cap(market_cap: float) -> str:
        """Classify stock by market cap"""
        for cap_type, (lower, upper) in StockAnalyzer.STOCK_CAPS.items():
            if lower <= market_cap < upper:
                return cap_type
        return 'unknown'

    @staticmethod
    def analyze_trend(
        close: pd.Series,
        high: pd.Series,
        low: pd.Series,
        volume: pd.Series,
        period: int = 20
    ) -> Dict:
        """
        Comprehensive trend analysis
        Returns probability scores for bullish/bearish scenarios
        """
        ti = TechnicalIndicators()
        
        sma_20 = ti.moving_average(close, 20)
        ema_12 = ti.exponential_moving_average(close, 12)
        ema_26 = ti.exponential_moving_average(close, 26)
        rsi = ti.rsi(close, 14)
        bb = ti.bollinger_bands(close, 20, 2.0)
        macd = ti.macd(close)
        atr = ti.atr(high, low, close, 14)
        
        current_price = close.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd['macd_line'].iloc[-1]
        current_signal = macd['signal_line'].iloc[-1]
        current_histogram = macd['histogram'].iloc[-1]
        current_atr = atr.iloc[-1]
        
        bb_upper = bb['upper_band'].iloc[-1]
        bb_lower = bb['lower_band'].iloc[-1]
        bb_middle = bb['middle_band'].iloc[-1]
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
        
        vol_analysis = ti.volume_analysis(volume, 20)
        
        last_close = close.iloc[-1]
        prev_close = close.iloc[-2] if len(close) > 1 else close.iloc[-1]
        price_change = last_close - prev_close
        price_change_percent = (price_change / prev_close * 100) if prev_close != 0 else 0
        
        bullish_score = 0
        bearish_score = 0
        
        if current_rsi < 30:
            bullish_score += 15
        elif current_rsi < 50:
            bullish_score += 8
        elif current_rsi > 70:
            bearish_score += 15
        elif current_rsi > 50:
            bearish_score += 8
        
        if current_macd > current_signal and current_histogram > 0:
            bullish_score += 15
        elif current_macd < current_signal and current_histogram < 0:
            bearish_score += 15
        
        if current_price > sma_20.iloc[-1] > ema_26.iloc[-1]:
            bullish_score += 15
        elif current_price < sma_20.iloc[-1] < ema_26.iloc[-1]:
            bearish_score += 15
        
        if bb_position < 0.25: 
            bullish_score += 10
        elif bb_position > 0.75:  
            bearish_score += 10
        
        if vol_analysis['is_high_volume']:
            if price_change > 0:
                bullish_score += 10
            else:
                bearish_score += 10
        
        total_score = bullish_score + bearish_score
        if total_score == 0:
            bullish_prob = 50
            bearish_prob = 50
        else:
            bullish_prob = (bullish_score / total_score) * 100
            bearish_prob = (bearish_score / total_score) * 100
        
        return {
            'current_price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'price_change_percent': round(price_change_percent, 2),
            'trend_direction': 'BULLISH' if bullish_prob > bearish_prob else 'BEARISH',
            'bullish_probability': round(bullish_prob, 1),
            'bearish_probability': round(bearish_prob, 1),
            'rsi': round(current_rsi, 1),
            'rsi_signal': 'Oversold' if current_rsi < 30 else 'Overbought' if current_rsi > 70 else 'Neutral',
            'macd_signal': 'Bullish' if current_histogram > 0 else 'Bearish',
            'volume_signal': 'High Volume' if vol_analysis['is_high_volume'] else 'Normal Volume',
            'volatility_atr': round(current_atr, 2),
            'bollinger_position': round(bb_position * 100, 1)
        }

    @staticmethod
    def generate_buy_signal(
        close: pd.Series,
        high: pd.Series,
        low: pd.Series,
        volume: pd.Series
    ) -> Dict:
        """
        Generate buy signal with confidence level
        """
        ti = TechnicalIndicators()
        rsi = ti.rsi(close, 14)
        bb = ti.bollinger_bands(close, 20, 2.0)
        macd = ti.macd(close)
        
        current_rsi = rsi.iloc[-1]
        current_price = close.iloc[-1]
        bb_lower = bb['lower_band'].iloc[-1]
        current_histogram = macd['histogram'].iloc[-1]
        
        signals = []
        confidence = 0
        
        if current_rsi < 30:
            signals.append('RSI in oversold zone (<30)')
            confidence += 25
        
        if current_price <= bb_lower * 1.01:  
            signals.append('Price near lower Bollinger Band')
            confidence += 20
        
        if current_histogram > 0:
            signals.append('MACD histogram positive')
            confidence += 20
        
        vol_analysis = ti.volume_analysis(volume, 20)
        if vol_analysis['is_high_volume']:
            signals.append('High volume confirmation')
            confidence += 15
        
        sma_20 = ti.moving_average(close, 20)
        if close.iloc[-2] < sma_20.iloc[-2] and current_price > sma_20.iloc[-1]:
            signals.append('Price crossed above SMA20')
            confidence += 20
        
        return {
            'buy_signal': confidence >= 50,
            'confidence_score': min(100, confidence),
            'signals': signals,
            'signal_count': len(signals)
        }

    @staticmethod
    def generate_sell_signal(
        close: pd.Series,
        high: pd.Series,
        low: pd.Series,
        volume: pd.Series
    ) -> Dict:
        """
        Generate sell signal with confidence level
        """
        ti = TechnicalIndicators()
        rsi = ti.rsi(close, 14)
        bb = ti.bollinger_bands(close, 20, 2.0)
        macd = ti.macd(close)
        
        current_rsi = rsi.iloc[-1]
        current_price = close.iloc[-1]
        bb_upper = bb['upper_band'].iloc[-1]
        current_histogram = macd['histogram'].iloc[-1]
        
        signals = []
        confidence = 0
        
        if current_rsi > 70:
            signals.append('RSI in overbought zone (>70)')
            confidence += 25
        
        if current_price >= bb_upper * 0.99:  
            signals.append('Price near upper Bollinger Band')
            confidence += 20
        
        if current_histogram < 0:
            signals.append('MACD histogram negative')
            confidence += 20
        
        vol_analysis = ti.volume_analysis(volume, 20)
        if vol_analysis['is_high_volume']:
            signals.append('High volume confirmation')
            confidence += 15
        
        sma_20 = ti.moving_average(close, 20)
        if close.iloc[-2] > sma_20.iloc[-2] and current_price < sma_20.iloc[-1]:
            signals.append('Price crossed below SMA20')
            confidence += 20
        
        return {
            'sell_signal': confidence >= 50,
            'confidence_score': min(100, confidence),
            'signals': signals,
            'signal_count': len(signals)
        }

    @staticmethod
    def get_support_resistance(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 20
    ) -> Dict:
        """
        Identify support and resistance levels
        """
        recent_highs = high.tail(period)
        recent_lows = low.tail(period)
        
        resistance = recent_highs.max()
        support = recent_lows.min()
        
        current_price = close.iloc[-1]
        distance_to_resistance = ((resistance - current_price) / current_price) * 100
        distance_to_support = ((current_price - support) / current_price) * 100
        
        return {
            'resistance': round(resistance, 2),
            'support': round(support, 2),
            'distance_to_resistance_percent': round(distance_to_resistance, 2),
            'distance_to_support_percent': round(distance_to_support, 2),
            'range': round(resistance - support, 2)
        }
