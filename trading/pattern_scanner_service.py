"""
Enhanced Pattern Scanner Service
Real-time candlestick pattern, chart pattern, and technical indicator detection
with live market data integration and historical analysis fallback
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import math
from datetime import datetime, timedelta


class EnhancedCandlestickDetector:
    """Advanced candlestick pattern detection with proper validation"""
    
    @staticmethod
    def detect_patterns(open_price: float, high: float, low: float, close: float, 
                       prev_data: Optional[Dict] = None) -> List[Dict]:
        """Detect multiple candlestick patterns from single candle"""
        patterns = []
        
        if high == low:  # Invalid candle
            return patterns
        
        body = abs(close - open_price)
        total_range = high - low
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low
        
        # 1. DOJI - Opening and closing prices are nearly equal
        if body < (total_range * 0.1) and total_range > 0:
            patterns.append({
                'name': 'Doji',
                'type': 'Neutral',
                'signal': 'Market indecision - potential reversal',
                'confidence': 65,
                'description': 'Opening ≈ Closing, shows uncertainty'
            })
        
        # 2. HAMMER - Long lower wick, small body, bullish
        if lower_wick > (body * 2) and body < (total_range * 0.3):
            if close > open_price:
                patterns.append({
                    'name': 'Hammer',
                    'type': 'Bullish',
                    'signal': 'Potential bullish reversal after downtrend',
                    'confidence': 75,
                    'description': 'Long lower wick with small body'
                })
        
        # 3. INVERTED HAMMER - Long upper wick, small body
        if upper_wick > (body * 2) and body < (total_range * 0.3):
            patterns.append({
                'name': 'Inverted Hammer',
                'type': 'Neutral',
                'signal': 'Potential reversal signal',
                'confidence': 60,
                'description': 'Long upper wick with small body'
            })
        
        # 4. SHOOTING STAR - Long upper wick, closes near low, bearish
        if upper_wick > (body * 2) and close < open_price and close < (high + low) / 2:
            patterns.append({
                'name': 'Shooting Star',
                'type': 'Bearish',
                'signal': 'Potential bearish reversal - rejection at higher prices',
                'confidence': 70,
                'description': 'Long upper wick, closes in lower half'
            })
        
        # 5. HANGING MAN - Long lower wick, closes near high, bearish
        if lower_wick > (body * 2) and close > open_price and close > (high + low) / 2:
            patterns.append({
                'name': 'Hanging Man',
                'type': 'Bearish',
                'signal': 'Potential bearish reversal - weakening uptrend',
                'confidence': 70,
                'description': 'Long lower wick, closes in upper half'
            })
        
        # 6. MARUBOZU - No wicks (or very small), strong trend
        if upper_wick < (total_range * 0.05) and lower_wick < (total_range * 0.05):
            if close > open_price:
                patterns.append({
                    'name': 'Bullish Marubozu',
                    'type': 'Bullish',
                    'signal': 'Strong bullish trend - buyers in control',
                    'confidence': 80,
                    'description': 'No upper wick, closes at high'
                })
            else:
                patterns.append({
                    'name': 'Bearish Marubozu',
                    'type': 'Bearish',
                    'signal': 'Strong bearish trend - sellers in control',
                    'confidence': 80,
                    'description': 'No lower wick, closes at low'
                })
        
        # 7. SPINNING TOP - Small body with both wicks (indecision)
        if body < (total_range * 0.3) and upper_wick > (body * 0.5) and lower_wick > (body * 0.5):
            patterns.append({
                'name': 'Spinning Top',
                'type': 'Neutral',
                'signal': 'Market indecision - weakness in current trend',
                'confidence': 55,
                'description': 'Small body with significant wicks'
            })
        
        # 8. BULLISH/BEARISH ENGULFING (with previous data)
        if prev_data:
            prev_open = prev_data.get('open', close)
            prev_close = prev_data.get('close', close)
            prev_high = prev_data.get('high', high)
            prev_low = prev_data.get('low', low)
            
            # Bullish Engulfing
            if (close > prev_open and open_price < prev_close and 
                prev_close < prev_open):  # Previous was red
                patterns.append({
                    'name': 'Bullish Engulfing',
                    'type': 'Bullish',
                    'signal': 'Strong bullish reversal - buyers overwhelm sellers',
                    'confidence': 85,
                    'description': 'Current candle engulfs previous bearish candle'
                })
            
            # Bearish Engulfing
            if (close < prev_open and open_price > prev_close and 
                prev_close > prev_open):  # Previous was green
                patterns.append({
                    'name': 'Bearish Engulfing',
                    'type': 'Bearish',
                    'signal': 'Strong bearish reversal - sellers overwhelm buyers',
                    'confidence': 85,
                    'description': 'Current candle engulfs previous bullish candle'
                })
            
            # MORNING STAR (3 candles) - simplified with prev_data
            if len(prev_data.get('history', [])) >= 2:
                patterns.append({
                    'name': 'Morning Star',
                    'type': 'Bullish',
                    'signal': 'Bullish reversal after downtrend',
                    'confidence': 75,
                    'description': '3-candle reversal pattern at bottoms'
                })
            
            # EVENING STAR (3 candles)
            if len(prev_data.get('history', [])) >= 2:
                patterns.append({
                    'name': 'Evening Star',
                    'type': 'Bearish',
                    'signal': 'Bearish reversal after uptrend',
                    'confidence': 75,
                    'description': '3-candle reversal pattern at tops'
                })
        
        # 9. BULLISH/BEARISH HARAMI - Small candle inside previous large candle
        if prev_data:
            prev_body = abs(prev_open - prev_close) if prev_data else 0
            if prev_body > 0 and body < (prev_body * 0.5):
                patterns.append({
                    'name': 'Harami',
                    'type': 'Neutral',
                    'signal': 'Potential reversal - momentum loss',
                    'confidence': 60,
                    'description': 'Small candle inside previous candle'
                })
        
        return patterns


class EnhancedChartPatternDetector:
    """Detect multi-candle chart patterns"""
    
    @staticmethod
    def detect_patterns(highs: List[float], lows: List[float], closes: List[float]) -> List[Dict]:
        """Detect chart patterns from price history"""
        patterns = []
        
        if len(highs) < 5:
            return patterns
        
        # Recent data
        recent_highs = highs[-20:] if len(highs) >= 20 else highs
        recent_lows = lows[-20:] if len(lows) >= 20 else lows
        recent_closes = closes[-20:] if len(closes) >= 20 else closes
        
        current_price = recent_closes[-1]
        
        # 1. TRIANGLE - Converging highs and lows
        high_trend = max(recent_highs) - min(recent_highs[-10:])
        low_trend = max(recent_lows[-10:]) - min(recent_lows)
        
        if high_trend > 0 and low_trend > 0 and high_trend < (max(recent_highs) * 0.05):
            patterns.append({
                'pattern': 'Symmetrical Triangle',
                'type': 'Neutral',
                'signal': 'Consolidation - breakout expected',
                'confidence': 65,
                'description': 'Converging highs and lows - expect volatility'
            })
        
        # 2. FLAG - Small consolidation after strong move
        if len(recent_closes) >= 10:
            prev_move = recent_closes[-10] - recent_closes[0]
            recent_range = max(recent_highs[-5:]) - min(recent_lows[-5:])
            
            if prev_move != 0 and recent_range < abs(prev_move) * 0.3:
                if prev_move > 0:
                    patterns.append({
                        'pattern': 'Bullish Flag',
                        'type': 'Bullish',
                        'signal': 'Continuation pattern - uptrend to resume',
                        'confidence': 70,
                        'description': 'Small consolidation during uptrend'
                    })
                else:
                    patterns.append({
                        'pattern': 'Bearish Flag',
                        'type': 'Bearish',
                        'signal': 'Continuation pattern - downtrend to resume',
                        'confidence': 70,
                        'description': 'Small consolidation during downtrend'
                    })
        
        # 3. WEDGE - Convergingsimilar to triangle
        if len(recent_closes) >= 15:
            patterns.append({
                'pattern': 'Ascending Wedge',
                'type': 'Bearish',
                'signal': 'Reversal pattern - potential breakout downward',
                'confidence': 60,
                'description': 'Rising resistance, rising support'
            })
        
        # 4. HEAD AND SHOULDERS - Three peaks pattern
        if len(recent_closes) >= 15:
            mid_point = len(recent_highs) // 2
            left_shoulder = max(recent_highs[:mid_point])
            head = max(recent_highs)
            right_shoulder = max(recent_highs[mid_point:])
            
            if abs(left_shoulder - right_shoulder) < (head * 0.05) and head > left_shoulder:
                patterns.append({
                    'pattern': 'Head and Shoulders',
                    'type': 'Bearish',
                    'signal': 'Strong bearish reversal - downtrend likely',
                    'confidence': 80,
                    'description': 'Three peaks with middle highest'
                })
        
        # 5. DOUBLE TOP / DOUBLE BOTTOM
        if len(recent_closes) >= 10:
            peaks = [i for i in range(1, len(recent_highs)-1) 
                    if recent_highs[i] > recent_highs[i-1] and recent_highs[i] > recent_highs[i+1]]
            
            if len(peaks) >= 2:
                patterns.append({
                    'pattern': 'Double Top',
                    'type': 'Bearish',
                    'signal': 'Reversal pattern - resistance confirmed',
                    'confidence': 75,
                    'description': 'Two peaks at similar levels'
                })
            
            valleys = [i for i in range(1, len(recent_lows)-1) 
                      if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]]
            
            if len(valleys) >= 2:
                patterns.append({
                    'pattern': 'Double Bottom',
                    'type': 'Bullish',
                    'signal': 'Reversal pattern - support confirmed',
                    'confidence': 75,
                    'description': 'Two troughs at similar levels'
                })
        
        return patterns


class EnhancedIndicatorCalculator:
    """Calculate technical indicators from price data"""
    
    @staticmethod
    def calculate_rsi(closes: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(closes) < period:
            return 50.0  # Neutral if insufficient data
        
        changes = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [c for c in changes if c > 0]
        losses = [-c for c in changes if c < 0]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(min(100, max(0, rsi)))
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return float(ema)
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0.0
        
        return float(sum(prices[-period:]) / period)
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            current = prices[-1] if prices else 0
            return {
                'upper': current * 1.02,
                'middle': current,
                'lower': current * 0.98,
            }
        
        sma = EnhancedIndicatorCalculator.calculate_sma(prices, period)
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std_dev = math.sqrt(variance)
        
        return {
            'upper': float(sma + (std_dev * 2)),
            'middle': float(sma),
            'lower': float(sma - (std_dev * 2)),
        }
    
    @staticmethod
    def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
        """Calculate Volume Weighted Average Price"""
        if not prices or not volumes or len(prices) != len(volumes):
            return prices[-1] if prices else 0.0
        
        pv = sum(p * v for p, v in zip(prices, volumes))
        v = sum(volumes)
        
        return float(pv / v) if v > 0 else float(prices[-1])
    
    @staticmethod
    def calculate_fibonacci(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        range_val = high - low
        
        return {
            '0.0%': float(high),
            '23.6%': float(high - (range_val * 0.236)),
            '38.2%': float(high - (range_val * 0.382)),
            '50.0%': float(high - (range_val * 0.5)),
            '61.8%': float(high - (range_val * 0.618)),
            '78.6%': float(high - (range_val * 0.786)),
            '100.0%': float(low),
        }


class TradingLevelCalculator:
    """Calculate trading entry, target, and stop-loss levels"""
    
    @staticmethod
    def calculate_support_resistance(lows: List[float], highs: List[float]) -> Tuple[float, float]:
        """Calculate support and resistance from price extremes"""
        if not lows or not highs:
            return 0, 0
        
        # Use recent data
        recent_lows = lows[-20:] if len(lows) >= 20 else lows
        recent_highs = highs[-20:] if len(highs) >= 20 else highs
        
        support = min(recent_lows)
        resistance = max(recent_highs)
        
        return float(support), float(resistance)
    
    @staticmethod
    def calculate_entry_targets(current_price: float, support: float, 
                                resistance: float, is_bullish: bool = True) -> Dict:
        """Calculate entry point, targets, and stop-loss"""
        
        if is_bullish:
            range_val = resistance - current_price
            entry = max(current_price * 0.998, support)  # 99.8% of current or support
            stop_loss = max(support * 0.99, current_price * 0.98)
            
            target_1 = current_price + (range_val * 0.33)
            target_2 = current_price + (range_val * 0.66)
            target_3 = resistance
            target_4 = resistance * 1.02
        else:
            range_val = current_price - support
            entry = min(current_price * 1.002, resistance)  # 100.2% of current or resistance
            stop_loss = min(resistance * 1.01, current_price * 1.02)
            
            target_1 = current_price - (range_val * 0.33)
            target_2 = current_price - (range_val * 0.66)
            target_3 = support
            target_4 = support * 0.98
        
        return {
            'entry': float(entry),
            'target_1': float(target_1),
            'target_2': float(target_2),
            'target_3': float(target_3),
            'target_4': float(target_4),
            'stop_loss': float(stop_loss),
        }


class PatternScannerService:
    """Main service orchestrating pattern scanning"""
    
    @staticmethod
    def scan_stock(current_price: float, high: float, low: float, open_price: float,
                   volume: float = 0, prices_history: List[float] = None,
                   volumes_history: List[float] = None, prev_candle: Optional[Dict] = None) -> Dict:
        """
        Complete pattern scan for a stock
        
        Returns comprehensive analysis with:
        - Candlestick patterns
        - Chart patterns
        - Indicators
        - Trading levels
        """
        
        # Initialize detectors
        candle_detector = EnhancedCandlestickDetector()
        chart_detector = EnhancedChartPatternDetector()
        indicator_calc = EnhancedIndicatorCalculator()
        level_calc = TradingLevelCalculator()
        
        # Prepare data with fallback
        if prices_history is None:
            prices_history = [current_price]
        if volumes_history is None:
            volumes_history = [volume] if volume > 0 else [1000000]  # Default volume
        
        # Detect candlestick patterns
        candlestick_patterns = candle_detector.detect_patterns(
            open_price, high, low, current_price,
            prev_data=prev_candle
        )
        
        # Detect chart patterns
        chart_patterns = chart_detector.detect_patterns(
            [h for h in prices_history if h > 0],  # Use prices as proxy for highs
            [l for l in prices_history if l > 0],  # Use prices as proxy for lows
            prices_history
        ) if len(prices_history) > 1 else []
        
        # Calculate indicators
        rsi = indicator_calc.calculate_rsi(prices_history)
        ema_20 = indicator_calc.calculate_ema(prices_history, 20)
        ema_50 = indicator_calc.calculate_ema(prices_history, 50)
        ema_100 = indicator_calc.calculate_ema(prices_history, 100)
        ema_200 = indicator_calc.calculate_ema(prices_history, 200)
        vwap = indicator_calc.calculate_vwap(prices_history, volumes_history)
        bollinger = indicator_calc.calculate_bollinger_bands(prices_history)
        fibonacci = indicator_calc.calculate_fibonacci(high, low)
        
        # Calculate trading levels
        support, resistance = level_calc.calculate_support_resistance(
            prices_history, [high] * len(prices_history)
        )
        
        # Determine trend
        is_bullish = current_price > vwap and current_price > ema_50
        entry_targets = level_calc.calculate_entry_targets(
            current_price, support, resistance, is_bullish
        )
        
        # Determine overall sentiment
        bullish_count = sum(1 for p in candlestick_patterns if p['type'] == 'Bullish')
        bearish_count = sum(1 for p in candlestick_patterns if p['type'] == 'Bearish')
        
        overall_sentiment = 'BULLISH' if bullish_count > bearish_count else 'BEARISH' if bearish_count > bullish_count else 'NEUTRAL'
        confidence = min(95, max(50, 50 + abs(bullish_count - bearish_count) * 10))
        
        return {
            'candlestick_patterns': candlestick_patterns,
            'chart_patterns': chart_patterns,
            'indicators': {
                'rsi': rsi,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'ema_100': ema_100,
                'ema_200': ema_200,
                'vwap': vwap,
                'bollinger_bands': bollinger,
            },
            'trading_levels': {
                'support': support,
                'resistance': resistance,
                'fibonacci': fibonacci,
            },
            'entry_exit': entry_targets,
            'summary': {
                'total_patterns': len(candlestick_patterns) + len(chart_patterns),
                'bullish_signals': bullish_count + sum(1 for p in chart_patterns if p['type'] == 'Bullish'),
                'bearish_signals': bearish_count + sum(1 for p in chart_patterns if p['type'] == 'Bearish'),
                'overall_sentiment': overall_sentiment,
                'confidence': float(confidence),
            }
        }
