"""
Technical Indicators Engine
Calculates all required indicators for signal generation
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# INDICATOR MODELS
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class TechnicalIndicators:
    """Container for all technical indicators"""
    symbol: str
    timestamp: str
    
    # Trend Indicators
    ema_20: float
    ema_50: float
    ema_100: float
    ema_200: float
    
    # Momentum Indicators
    rsi: float  # 0-100
    rsi_signal: str  # OVERBOUGHT, OVERSOLD, NEUTRAL
    
    # MACD
    macd_line: float
    macd_signal: float
    macd_histogram: float
    macd_signal_str: str  # BULLISH, BEARISH
    
    # ATR (Volatility)
    atr: float
    atr_percent: float
    
    # Volume
    vwap: float
    volume_ma: float
    volume_trend: str  # INCREASING, DECREASING, NEUTRAL
    
    # Support & Resistance
    support_1: float
    support_2: float
    resistance_1: float
    resistance_2: float
    
    # Pivot Points
    pivot: float
    pp_support: float
    pp_resistance: float
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "trend": {
                "ema_20": round(self.ema_20, 2),
                "ema_50": round(self.ema_50, 2),
                "ema_100": round(self.ema_100, 2),
                "ema_200": round(self.ema_200, 2),
            },
            "momentum": {
                "rsi": round(self.rsi, 2),
                "rsi_signal": self.rsi_signal,
                "macd_line": round(self.macd_line, 4),
                "macd_signal": round(self.macd_signal, 4),
                "macd_histogram": round(self.macd_histogram, 4),
                "macd_signal": self.macd_signal_str,
            },
            "volatility": {
                "atr": round(self.atr, 2),
                "atr_percent": round(self.atr_percent, 2),
            },
            "volume": {
                "vwap": round(self.vwap, 2),
                "volume_ma": round(self.volume_ma, 0),
                "volume_trend": self.volume_trend,
            },
            "levels": {
                "support_1": round(self.support_1, 2),
                "support_2": round(self.support_2, 2),
                "resistance_1": round(self.resistance_1, 2),
                "resistance_2": round(self.resistance_2, 2),
                "pivot": round(self.pivot, 2),
            }
        }


# ═══════════════════════════════════════════════════════════════════════
# TECHNICAL INDICATORS ENGINE
# ═══════════════════════════════════════════════════════════════════════

class TechnicalIndicatorsEngine:
    """Calculate all technical indicators"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    # ─────────────────────────────────────────────────────────────────
    # TREND INDICATORS
    # ─────────────────────────────────────────────────────────────────
    
    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices
        
        multiplier = 2 / (period + 1)
        ema = [np.mean(prices[:period])]  # First EMA is SMA
        
        for price in prices[period:]:
            ema.append(price * multiplier + ema[-1] * (1 - multiplier))
        
        return ema
    
    def calculate_sma(self, prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        return [np.mean(prices[max(0, i-period+1):i+1]) for i in range(len(prices))]
    
    # ─────────────────────────────────────────────────────────────────
    # MOMENTUM INDICATORS
    # ─────────────────────────────────────────────────────────────────
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> Tuple[float, str]:
        """
        Calculate Relative Strength Index (RSI)
        Returns: (rsi_value, signal)
        """
        if len(prices) < period + 1:
            return 50.0, "NEUTRAL"
        
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = 100.0 - 100.0 / (1.0 + rs) if rs != 0 else 50.0
        
        # Determine signal
        if rsi >= 70:
            signal = "OVERBOUGHT"
        elif rsi <= 30:
            signal = "OVERSOLD"
        else:
            signal = "NEUTRAL"
        
        return float(rsi), signal
    
    def calculate_macd(self, prices: List[float]) -> Tuple[float, float, float, str]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Returns: (macd_line, signal_line, histogram, signal)
        """
        if len(prices) < 26:
            return 0.0, 0.0, 0.0, "NEUTRAL"
        
        # Calculate EMAs
        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        
        # MACD line = EMA12 - EMA26
        min_len = min(len(ema_12), len(ema_26))
        macd_line = [ema_12[i] - ema_26[i] for i in range(-min_len, 0)]
        
        # Signal line = 9-period EMA of MACD
        if len(macd_line) < 9:
            signal_line = macd_line
        else:
            signal_line = self.calculate_ema(macd_line, 9)
        
        # Histogram
        if len(macd_line) == 0 or len(signal_line) == 0:
            return 0.0, 0.0, 0.0, "NEUTRAL"
        
        histogram = macd_line[-1] - signal_line[-1]
        macd_value = macd_line[-1]
        signal_value = signal_line[-1]
        
        # Signal: BULLISH if MACD > Signal, BEARISH otherwise
        signal = "BULLISH" if histogram > 0 else "BEARISH"
        
        return float(macd_value), float(signal_value), float(histogram), signal
    
    # ─────────────────────────────────────────────────────────────────
    # VOLATILITY INDICATORS
    # ─────────────────────────────────────────────────────────────────
    
    def calculate_atr(self, high: List[float], low: List[float], 
                     close: List[float], period: int = 14) -> Tuple[float, float]:
        """
        Calculate Average True Range (ATR)
        Returns: (atr_value, atr_percent)
        """
        if len(high) < period:
            return 0.0, 0.0
        
        tr_values = []
        for i in range(1, len(high)):
            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )
            tr_values.append(tr)
        
        atr = np.mean(tr_values[-period:])
        atr_percent = (atr / close[-1] * 100) if close[-1] != 0 else 0
        
        return float(atr), float(atr_percent)
    
    # ─────────────────────────────────────────────────────────────────
    # VOLUME INDICATORS
    # ─────────────────────────────────────────────────────────────────
    
    def calculate_vwap(self, high: List[float], low: List[float], 
                      close: List[float], volume: List[int]) -> float:
        """
        Calculate Volume Weighted Average Price (VWAP)
        Used for intraday trading
        """
        if len(close) < 1:
            return 0.0
        
        typical_price = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
        
        vwap_numerator = sum(tp * v for tp, v in zip(typical_price, volume))
        vwap_denominator = sum(volume)
        
        vwap = vwap_numerator / vwap_denominator if vwap_denominator > 0 else close[-1]
        
        return float(vwap)
    
    def calculate_volume_trend(self, volume: List[int], period: int = 20) -> str:
        """Analyze volume trend"""
        if len(volume) < period:
            return "NEUTRAL"
        
        recent_avg = np.mean(volume[-period:])
        previous_avg = np.mean(volume[-period*2:-period])
        
        change_percent = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        
        if change_percent > 10:
            return "INCREASING"
        elif change_percent < -10:
            return "DECREASING"
        else:
            return "NEUTRAL"
    
    # ─────────────────────────────────────────────────────────────────
    # SUPPORT & RESISTANCE
    # ─────────────────────────────────────────────────────────────────
    
    def calculate_support_resistance(self, high: List[float], 
                                    low: List[float]) -> Tuple[float, float, float, float]:
        """
        Calculate support and resistance levels
        Using recent highs and lows
        """
        if len(high) < 20:
            return 0.0, 0.0, 0.0, 0.0
        
        recent_high = max(high[-20:])
        recent_low = min(low[-20:])
        
        # Resistance levels
        resistance_1 = recent_high
        resistance_2 = recent_high + (recent_high - recent_low) * 0.5
        
        # Support levels
        support_1 = recent_low
        support_2 = recent_low - (recent_high - recent_low) * 0.5
        
        return float(support_1), float(support_2), float(resistance_1), float(resistance_2)
    
    def calculate_pivot_points(self, high: float, low: float, close: float) -> Tuple[float, float, float]:
        """
        Calculate Pivot Points
        Standard pivot calculation
        """
        pivot = (high + low + close) / 3
        support = 2 * pivot - high
        resistance = 2 * pivot - low
        
        return float(pivot), float(support), float(resistance)
    
    # ─────────────────────────────────────────────────────────────────
    # PATTERN DETECTION
    # ─────────────────────────────────────────────────────────────────
    
    def detect_candlestick_patterns(self, data: List[Dict]) -> List[str]:
        """Detect candlestick patterns"""
        patterns = []
        
        if len(data) < 3:
            return patterns
        
        # Get last 3 candles
        c1, c2, c3 = data[-3], data[-2], data[-1]
        
        # Hammer (bullish reversal)
        body_size = abs(c3["close"] - c3["open"])
        lower_wick = c3["open"] - c3["low"] if c3["close"] > c3["open"] else c3["close"] - c3["low"]
        if lower_wick > 2 * body_size and body_size < (c3["high"] - c3["low"]) * 0.3:
            patterns.append("HAMMER")
        
        # Doji (indecision)
        if body_size < (c3["high"] - c3["low"]) * 0.1:
            patterns.append("DOJI")
        
        # Engulfing (bullish/bearish)
        if c3["close"] > c2["high"] and c3["open"] < c2["low"]:
            patterns.append("BULLISH_ENGULFING")
        elif c3["close"] < c2["low"] and c3["open"] > c2["high"]:
            patterns.append("BEARISH_ENGULFING")
        
        return patterns
    
    # ─────────────────────────────────────────────────────────────────
    # MAIN CALCULATION METHOD
    # ─────────────────────────────────────────────────────────────────
    
    def calculate_all(self, candle_data: List[Dict]) -> Optional[TechnicalIndicators]:
        """
        Calculate all indicators from OHLCV data
        
        Args:
            candle_data: List of dicts with open, high, low, close, volume
        
        Returns:
            TechnicalIndicators object
        """
        try:
            if len(candle_data) < 50:
                logger.warning(f"Insufficient data for {self.symbol}: {len(candle_data)} candles")
                return None
            
            # Extract OHLCV
            closes = [c["close"] for c in candle_data]
            opens = [c["open"] for c in candle_data]
            highs = [c["high"] for c in candle_data]
            lows = [c["low"] for c in candle_data]
            volumes = [c["volume"] for c in candle_data]
            
            # Calculate all indicators
            ema_20 = self.calculate_ema(closes, 20)[-1] if len(closes) >= 20 else closes[-1]
            ema_50 = self.calculate_ema(closes, 50)[-1] if len(closes) >= 50 else closes[-1]
            ema_100 = self.calculate_ema(closes, 100)[-1] if len(closes) >= 100 else closes[-1]
            ema_200 = self.calculate_ema(closes, 200)[-1] if len(closes) >= 200 else closes[-1]
            
            rsi, rsi_signal = self.calculate_rsi(closes)
            macd_line, macd_signal, macd_histogram, macd_signal_str = self.calculate_macd(closes)
            atr, atr_percent = self.calculate_atr(highs, lows, closes)
            vwap = self.calculate_vwap(highs, lows, closes, volumes)
            volume_ma = np.mean(volumes[-20:])
            volume_trend = self.calculate_volume_trend(volumes)
            
            support_1, support_2, resistance_1, resistance_2 = self.calculate_support_resistance(highs, lows)
            pivot, pp_support, pp_resistance = self.calculate_pivot_points(highs[-1], lows[-1], closes[-1])
            
            indicators = TechnicalIndicators(
                symbol=self.symbol,
                timestamp=pd.Timestamp.now().isoformat(),
                ema_20=ema_20,
                ema_50=ema_50,
                ema_100=ema_100,
                ema_200=ema_200,
                rsi=rsi,
                rsi_signal=rsi_signal,
                macd_line=macd_line,
                macd_signal=macd_signal,
                macd_histogram=macd_histogram,
                macd_signal_str=macd_signal_str,
                atr=atr,
                atr_percent=atr_percent,
                vwap=vwap,
                volume_ma=volume_ma,
                volume_trend=volume_trend,
                support_1=support_1,
                support_2=support_2,
                resistance_1=resistance_1,
                resistance_2=resistance_2,
                pivot=pivot,
                pp_support=pp_support,
                pp_resistance=pp_resistance
            )
            
            logger.info(f"✓ Calculated indicators for {self.symbol}")
            return indicators
        
        except Exception as e:
            logger.error(f"Error calculating indicators for {self.symbol}: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════
# PATTERN DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════

class PatternDetectionEngine:
    """Detect chart and candlestick patterns"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def detect_chart_patterns(self, highs: List[float], lows: List[float], 
                            closes: List[float]) -> Dict[str, bool]:
        """Detect chart patterns"""
        patterns = {}
        
        if len(closes) < 20:
            return patterns
        
        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        recent_closes = closes[-20:]
        
        # Double Bottom (bullish reversal)
        patterns["double_bottom"] = (
            len(recent_lows) >= 10 and 
            recent_lows[0] == recent_lows[-1] and 
            recent_closes[-1] > recent_closes[0]
        )
        
        # Double Top (bearish reversal)
        patterns["double_top"] = (
            len(recent_highs) >= 10 and 
            recent_highs[0] == recent_highs[-1] and 
            recent_closes[-1] < recent_closes[0]
        )
        
        # Uptrend (higher highs and higher lows)
        patterns["uptrend"] = all(
            recent_highs[i] <= recent_highs[i+1] and recent_lows[i] <= recent_lows[i+1]
            for i in range(len(recent_highs)-5)
        )
        
        # Downtrend (lower highs and lower lows)
        patterns["downtrend"] = all(
            recent_highs[i] >= recent_highs[i+1] and recent_lows[i] >= recent_lows[i+1]
            for i in range(len(recent_highs)-5)
        )
        
        return patterns
    
    def detect_all_patterns(self, candle_data: List[Dict]) -> Dict:
        """Detect all patterns"""
        if len(candle_data) < 20:
            return {"patterns": [], "warnings": ["Insufficient data for pattern detection"]}
        
        highs = [c["high"] for c in candle_data]
        lows = [c["low"] for c in candle_data]
        closes = [c["close"] for c in candle_data]
        
        chart_patterns = self.detect_chart_patterns(highs, lows, closes)
        
        # Filter out False patterns
        detected = [p for p, detected in chart_patterns.items() if detected]
        
        return {
            "patterns": detected,
            "chart_analysis": chart_patterns
        }
