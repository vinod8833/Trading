"""
Technical Analysis Pattern Detection Service
Detects candlestick patterns, chart patterns, and calculates trading levels
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import math


class CandlestickPatternDetector:
    """Detects single and multi-candle patterns"""
    
    @staticmethod
    def detect_doji(open_price: float, high: float, low: float, close: float) -> bool:
        """Doji: Opening and closing prices are equal or very close"""
        body = abs(close - open_price)
        total_range = high - low
        return body < (total_range * 0.1)  # Body less than 10% of total range
    
    @staticmethod
    def detect_hammer(open_price: float, high: float, low: float, close: float, is_bullish: bool) -> bool:
        """Hammer: Long lower wick, small body. Bullish if after downtrend"""
        body = abs(close - open_price)
        lower_wick = open_price - low if is_bullish else close - low
        total_range = high - low
        
        return (lower_wick > body * 2) and (body < total_range * 0.3)
    
    @staticmethod
    def detect_inverted_hammer(open_price: float, high: float, low: float, close: float) -> bool:
        """Inverted Hammer: Long upper wick, small body"""
        body = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        total_range = high - low
        
        return (upper_wick > body * 2) and (body < total_range * 0.3)
    
    @staticmethod
    def detect_shooting_star(open_price: float, high: float, low: float, close: float) -> bool:
        """Shooting Star: Long upper wick, small body, closes near bottom"""
        body = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        total_range = high - low
        
        return (upper_wick > body * 2) and (body < total_range * 0.3) and (close < open_price)
    
    @staticmethod
    def detect_hanging_man(open_price: float, high: float, low: float, close: float) -> bool:
        """Hanging Man: Long lower wick, small body, closes near top"""
        body = abs(close - open_price)
        lower_wick = min(open_price, close) - low
        total_range = high - low
        
        return (lower_wick > body * 2) and (body < total_range * 0.3) and (close > open_price)
    
    @staticmethod
    def detect_engulfing(prev_open: float, prev_close: float, prev_high: float, prev_low: float,
                        open_price: float, close: float, high: float, low: float, is_bullish: bool) -> bool:
        """Engulfing: Current candle fully engulfs previous candle"""
        if is_bullish:
            # Bullish Engulfing: Green candle engulfs red candle
            return close > prev_open and open_price < prev_close
        else:
            # Bearish Engulfing: Red candle engulfs green candle
            return close < prev_open and open_price > prev_close
    
    @staticmethod
    def detect_piercing(prev_open: float, prev_close: float, open_price: float, close: float) -> bool:
        """Piercing: Green candle closes above 50% of previous red candle"""
        if prev_open > prev_close:  # Previous was red
            midpoint = prev_open - ((prev_open - prev_close) / 2)
            return close > midpoint and open_price < prev_close
        return False
    
    @staticmethod
    def detect_harami(prev_open: float, prev_close: float, open_price: float, close: float,
                     prev_high: float, prev_low: float, high: float, low: float) -> bool:
        """Harami: Small candle inside previous larger candle"""
        prev_body = abs(prev_open - prev_close)
        curr_body = abs(close - open_price)
        
        # Current candle body is smaller and inside previous candle
        return (curr_body < prev_body * 0.5 and 
                min(open_price, close) > prev_low and 
                max(open_price, close) < prev_high)


class ChartPatternDetector:
    """Detects multi-candle chart patterns"""
    
    @staticmethod
    def detect_ascending_triangle(prices: List[float], highs: List[float], lows: List[float], period: int = 20) -> Dict:
        """Ascending Triangle: Flat resistance, rising support"""
        if len(prices) < period:
            return {}
        
        recent_highs = highs[-period:]
        recent_lows = lows[-period:]
        
        # Check if highs are relatively flat (resistance)
        max_high = max(recent_highs)
        min_high = min(recent_highs[-5:])  # Last 5 highs
        
        # Check if lows are ascending
        is_ascending = all(recent_lows[i] <= recent_lows[i+1] for i in range(len(recent_lows)-2))
        
        if abs(max_high - min_high) < (max_high * 0.02) and is_ascending:
            return {
                'pattern': 'Ascending Triangle',
                'type': 'Bullish',
                'resistance': max_high,
                'support': min(recent_lows),
                'breakout_direction': 'UP'
            }
        return {}
    
    @staticmethod
    def detect_descending_triangle(prices: List[float], highs: List[float], lows: List[float], period: int = 20) -> Dict:
        """Descending Triangle: Flat support, falling resistance"""
        if len(prices) < period:
            return {}
        
        recent_highs = highs[-period:]
        recent_lows = lows[-period:]
        
        # Check if lows are relatively flat (support)
        max_low = max(recent_lows[-5:])
        min_low = min(recent_lows)
        
        # Check if highs are descending
        is_descending = all(recent_highs[i] >= recent_highs[i+1] for i in range(len(recent_highs)-2))
        
        if abs(max_low - min_low) < (min_low * 0.02) and is_descending:
            return {
                'pattern': 'Descending Triangle',
                'type': 'Bearish',
                'support': min_low,
                'resistance': max(recent_highs),
                'breakout_direction': 'DOWN'
            }
        return {}
    
    @staticmethod
    def detect_double_top(prices: List[float], highs: List[float], period: int = 30) -> Dict:
        """Double Top: Two peaks at similar height"""
        if len(prices) < period:
            return {}
        
        recent_highs = highs[-period:]
        
        # Find two significant peaks
        peaks = []
        for i in range(1, len(recent_highs)-1):
            if recent_highs[i] > recent_highs[i-1] and recent_highs[i] > recent_highs[i+1]:
                peaks.append((i, recent_highs[i]))
        
        if len(peaks) >= 2:
            peak1_idx, peak1_val = peaks[-2]
            peak2_idx, peak2_val = peaks[-1]
            
            if abs(peak1_val - peak2_val) < (max(peak1_val, peak2_val) * 0.02):
                # Find neckline (valley between peaks)
                neckline = min(recent_highs[peak1_idx:peak2_idx])
                
                return {
                    'pattern': 'Double Top',
                    'type': 'Bearish',
                    'resistance': max(peak1_val, peak2_val),
                    'neckline': neckline,
                    'breakout_direction': 'DOWN'
                }
        return {}
    
    @staticmethod
    def detect_double_bottom(prices: List[float], lows: List[float], period: int = 30) -> Dict:
        """Double Bottom: Two troughs at similar height"""
        if len(prices) < period:
            return {}
        
        recent_lows = lows[-period:]
        
        # Find two significant troughs
        troughs = []
        for i in range(1, len(recent_lows)-1):
            if recent_lows[i] < recent_lows[i-1] and recent_lows[i] < recent_lows[i+1]:
                troughs.append((i, recent_lows[i]))
        
        if len(troughs) >= 2:
            trough1_idx, trough1_val = troughs[-2]
            trough2_idx, trough2_val = troughs[-1]
            
            if abs(trough1_val - trough2_val) < (max(trough1_val, trough2_val) * 0.02):
                # Find neckline (peak between troughs)
                neckline = max(recent_lows[trough1_idx:trough2_idx])
                
                return {
                    'pattern': 'Double Bottom',
                    'type': 'Bullish',
                    'support': min(trough1_val, trough2_val),
                    'neckline': neckline,
                    'breakout_direction': 'UP'
                }
        return {}


class TradingLevelCalculator:
    """Calculates entry, target, and stop-loss levels based on patterns"""
    
    @staticmethod
    def calculate_levels_from_pattern(pattern: Dict, current_price: float, pattern_type: str = 'bullish') -> Dict:
        """Calculate entry, target, and stop-loss based on detected pattern"""
        current_price = float(current_price)
        support = float(pattern.get('support', pattern.get('neckline', current_price * 0.95)))
        resistance = float(pattern.get('resistance', current_price * 1.05))
        
        levels = {
            'entry': current_price,
            'stop_loss': 0,
            'target_1': 0,
            'target_2': 0,
            'target_3': 0,
            'target_4': 0,
        }
        
        if pattern_type == 'bullish':
            levels['stop_loss'] = support * 0.98  # 2% below support
            price_range = resistance - current_price
            
            levels['target_1'] = current_price + (price_range * 0.25)
            levels['target_2'] = current_price + (price_range * 0.50)
            levels['target_3'] = current_price + (price_range * 0.75)
            levels['target_4'] = resistance * 1.05
            
        else:  # bearish
            levels['stop_loss'] = resistance * 1.02  # 2% above resistance
            price_range = current_price - support
            
            levels['target_1'] = current_price - (price_range * 0.25)
            levels['target_2'] = current_price - (price_range * 0.50)
            levels['target_3'] = current_price - (price_range * 0.75)
            levels['target_4'] = support * 0.95
        
        return levels
    
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        
        return {
            '0%': high,
            '23.6%': high - (diff * 0.236),
            '38.2%': high - (diff * 0.382),
            '50%': high - (diff * 0.5),
            '61.8%': high - (diff * 0.618),
            '78.6%': high - (diff * 0.786),
            '100%': low,
        }
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], period: int = 20) -> Tuple[float, float]:
        """Calculate dynamic support and resistance levels"""
        if len(prices) < period:
            return prices[-1] * 0.95, prices[-1] * 1.05
        
        recent = prices[-period:]
        support = min(recent)
        resistance = max(recent)
        
        return support, resistance


class IndicatorCalculator:
    """Calculates technical indicators: VWAP, EMA, RSI, Bollinger Bands"""
    
    @staticmethod
    def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
        """Calculate VWAP (Volume Weighted Average Price)"""
        if not prices or not volumes:
            return prices[-1] if prices else 0
        
        typical_price = sum(p / len(prices) for p in prices) if prices else 0
        cum_volume = sum(volumes) if volumes else 1
        
        vwap = sum(prices[i] * volumes[i] for i in range(len(prices))) / cum_volume if cum_volume > 0 else prices[-1]
        return vwap
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate EMA (Exponential Moving Average)"""
        if len(prices) < period:
            return prices
        
        ema_values = []
        multiplier = 2 / (period + 1)
        
        # Calculate SMA for first period
        sma = sum(prices[:period]) / period
        ema_values.append(sma)
        
        # Calculate EMA
        for price in prices[period:]:
            ema = (price * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50  # Default neutral
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {}
        
        recent = prices[-period:]
        sma = sum(recent) / period
        
        # Calculate standard deviation
        variance = sum((p - sma) ** 2 for p in recent) / period
        std = math.sqrt(variance)
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev),
        }


class ScannerLogic:
    """Implements scanner logic for pattern and signal detection"""
    
    @staticmethod
    def scan_stock(prices: List[float], highs: List[float], lows: List[float], 
                  volumes: List[float], open_prices: List[float], close_prices: List[float]) -> Dict:
        """Comprehensive scan of stock for patterns and signals"""
        
        results = {
            'candlestick_patterns': [],
            'chart_patterns': [],
            'indicators': {},
            'trading_levels': {},
            'signals': []
        }
        
        if len(prices) < 5:
            return results
        
        current_price = prices[-1]
        
        # Detect candlestick patterns
        candle_detector = CandlestickPatternDetector()
        
        if candle_detector.detect_doji(open_prices[-1], highs[-1], lows[-1], close_prices[-1]):
            results['candlestick_patterns'].append({
                'name': 'Doji',
                'signal': 'Indecision - Wait for confirmation',
                'confidence': 50
            })
        
        if candle_detector.detect_hammer(open_prices[-1], highs[-1], lows[-1], close_prices[-1], True):
            results['candlestick_patterns'].append({
                'name': 'Hammer',
                'signal': 'BUY - Bullish reversal',
                'confidence': 70,
                'type': 'Bullish'
            })
        
        # Detect chart patterns
        chart_detector = ChartPatternDetector()
        
        asc_triangle = chart_detector.detect_ascending_triangle(prices, highs, lows)
        if asc_triangle:
            results['chart_patterns'].append(asc_triangle)
        
        dbl_bottom = chart_detector.detect_double_bottom(prices, lows)
        if dbl_bottom:
            results['chart_patterns'].append(dbl_bottom)
        
        # Calculate indicators
        calc = IndicatorCalculator()
        
        ema_20 = calc.calculate_ema(prices, 20)
        ema_50 = calc.calculate_ema(prices, 50)
        
        results['indicators'] = {
            'vwap': calc.calculate_vwap(prices, volumes),
            'ema_20': ema_20[-1] if ema_20 else current_price,
            'ema_50': ema_50[-1] if ema_50 else current_price,
            'rsi': calc.calculate_rsi(prices),
            'bollinger_bands': calc.calculate_bollinger_bands(prices),
        }
        
        # Calculate trading levels
        level_calc = TradingLevelCalculator()
        support, resistance = level_calc.calculate_support_resistance(prices)
        
        results['trading_levels'] = {
            'support': support,
            'resistance': resistance,
            'fibonacci': level_calc.calculate_fibonacci_levels(max(highs[-20:]), min(lows[-20:])),
        }
        
        return results
