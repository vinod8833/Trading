import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta
from .technical_analysis import CandlestickPatternDetector, ChartPatternDetector
from .services import TechnicalAnalysisService

logger = logging.getLogger(__name__)


class AISignalGenerator:
    """
    Generates AI-powered trading signals with confidence ranges
    
    Signals are based on:
    - Technical analysis patterns
    - Volume analysis
    - Trend analysis
    - Support/resistance levels
    - Risk-reward ratios
    
    NOT predictions: these are calculated probabilities based on historical patterns
    """
    
    SIGNAL_TYPES = {
        'STRONG_BUY': (0.75, 1.0),     
        'BUY': (0.60, 0.74),           
        'NEUTRAL': (0.40, 0.59),        
        'SELL': (0.26, 0.39),          
        'STRONG_SELL': (0.0, 0.25),     
    }
    
    @classmethod
    def generate_signal(
        cls,
        symbol: str,
        prices: List[float],
        volumes: List[int],
        highs: List[float],
        lows: List[float],
        current_price: float,
    ) -> Dict:
        """
        Generate comprehensive trading signal
        
        Returns: {
            'symbol': 'INFY',
            'signal': 'BUY' | 'SELL' | 'NEUTRAL',
            'confidence': 0.75,  # 0-1 range
            'confidence_range': (0.65, 0.85),  # Min-max confidence
            'entry_price': 1650.00,
            'target_price': 1700.00,
            'stop_loss': 1620.00,
            'risk_reward_ratio': 2.5,
            'factors': {
                'technical_patterns': ['Bullish Engulfing', 'Golden Cross'],
                'volume_signal': 'INCREASING',
                'trend': 'UPTREND',
                'momentum': 'STRONG_POSITIVE',
                'volatility': 'MODERATE',
            },
            'warning_flags': ['High volume required for breakout'],
            'probability_analysis': {
                'uptrend_probability': 0.72,
                'breakout_probability': 0.68,
                'support_hold_probability': 0.85,
            },
            'timestamp': datetime,
            'data_quality': 'HIGH',
            'confidence_reason': 'Multiple bullish patterns with increasing volume',
        }
        """
        try:
            if len(prices) < 50:
                return cls._insufficient_data_signal(symbol, current_price)
            
            technical_score = cls._analyze_technical_patterns(prices, highs, lows)
            volume_score = cls._analyze_volume(volumes)
            trend_score = cls._analyze_trend(prices)
            momentum_score = cls._analyze_momentum(prices)
            volatility_score = cls._analyze_volatility(prices)
            
            entry_price = current_price
            target_price, stop_loss = cls._calculate_levels(
                prices, highs, lows, technical_score, trend_score
            )
            
            confidence = cls._calculate_confidence(
                technical_score, volume_score, trend_score, momentum_score, volatility_score
            )
            
            signal_type = cls._get_signal_type(confidence)
            
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            warnings = cls._generate_warnings(
                prices, volumes, confidence, risk_reward_ratio
            )
            
            probabilities = cls._calculate_probabilities(
                technical_score, volume_score, trend_score
            )
            
            return {
                'symbol': symbol,
                'signal': signal_type,
                'confidence': float(confidence),
                'confidence_range': cls.SIGNAL_TYPES[signal_type],
                'entry_price': float(entry_price),
                'target_price': float(target_price),
                'stop_loss': float(stop_loss),
                'risk_reward_ratio': float(risk_reward_ratio),
                'factors': {
                    'technical_patterns': technical_score.get('patterns', []),
                    'volume_signal': volume_score.get('signal', 'NEUTRAL'),
                    'trend': trend_score.get('trend_type', 'NEUTRAL'),
                    'momentum': momentum_score.get('momentum_type', 'NEUTRAL'),
                    'volatility': volatility_score.get('volatility_level', 'MODERATE'),
                },
                'warning_flags': warnings,
                'probability_analysis': probabilities,
                'timestamp': datetime.now().isoformat(),
                'data_quality': 'HIGH' if len(prices) > 100 else 'ADEQUATE',
                'confidence_reason': cls._generate_confidence_reason(
                    technical_score, volume_score, confidence
                ),
                'disclaimer': 'This is a probability-based analysis, NOT a guarantee. Always use stop-losses.',
            }
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            return cls._error_signal(symbol, current_price, str(e))
    
    @classmethod
    def _analyze_technical_patterns(cls, prices: List[float], highs: List[float], lows: List[float]) -> Dict:
        """Analyze technical patterns"""
        patterns = []
        score = 0.5  
        
        prices_df = pd.Series(prices)
        rsi = TechnicalAnalysisService.calculate_rsi(prices)
        bb_upper, bb_middle, bb_lower = TechnicalAnalysisService.calculate_bollinger_bands(prices)
        ma_20 = TechnicalAnalysisService.calculate_moving_average(prices, 20)
        ma_50 = TechnicalAnalysisService.calculate_moving_average(prices, 50)
        
        if rsi < 30:
            patterns.append('Oversold (RSI < 30)')
            score += 0.15
        elif rsi > 70:
            patterns.append('Overbought (RSI > 70)')
            score -= 0.15
        
        if ma_20 and ma_50:
            if ma_20 > ma_50 * 1.01:
                patterns.append('Golden Cross (20MA > 50MA)')
                score += 0.15
            elif ma_20 < ma_50 * 0.99:
                patterns.append('Death Cross (20MA < 50MA)')
                score -= 0.15
        
        if bb_lower and bb_upper:
            current = prices[-1]
            if current > bb_upper * 0.98:
                patterns.append('Price near BB Upper')
                score -= 0.05
            elif current < bb_lower * 1.02:
                patterns.append('Price near BB Lower')
                score += 0.05
        
        if len(highs) >= 20:
            asc_tri = ChartPatternDetector.detect_ascending_triangle(prices, highs, lows)
            if asc_tri:
                patterns.append('Ascending Triangle (Bullish)')
                score += 0.20
            
            desc_tri = ChartPatternDetector.detect_descending_triangle(prices, highs, lows)
            if desc_tri:
                patterns.append('Descending Triangle (Bearish)')
                score -= 0.20
        
        if len(prices) >= 4:
            current = prices[-1]
            previous = prices[-2]
            if current > previous * 1.01:
                patterns.append('Bullish Candle')
                score += 0.05
            elif current < previous * 0.99:
                patterns.append('Bearish Candle')
                score -= 0.05
        
        score = max(0.0, min(1.0, score))
        
        return {
            'patterns': patterns,
            'score': score,
            'rsi': float(rsi),
            'ma_20': float(ma_20) if ma_20 else None,
            'ma_50': float(ma_50) if ma_50 else None,
        }
    
    @classmethod
    def _analyze_volume(cls, volumes: List[int]) -> Dict:
        """Analyze volume trends"""
        if len(volumes) < 20:
            return {'signal': 'NEUTRAL', 'score': 0.5}
        
        recent_vol = np.mean(volumes[-5:])
        historical_vol = np.mean(volumes[-20:-5])
        
        score = 0.5
        signal = 'NEUTRAL'
        
        if recent_vol > historical_vol * 1.3:  
            signal = 'INCREASING'
            score = 0.65
        elif recent_vol < historical_vol * 0.7:  
            signal = 'DECREASING'
            score = 0.35
        
        return {
            'signal': signal,
            'score': score,
            'recent_average': float(recent_vol),
            'historical_average': float(historical_vol),
            'volume_trend': float(recent_vol / historical_vol) if historical_vol > 0 else 1.0,
        }
    
    @classmethod
    def _analyze_trend(cls, prices: List[float]) -> Dict:
        """Analyze price trend"""
        if len(prices) < 50:
            return {'trend_type': 'NEUTRAL', 'score': 0.5}
        
        prices_array = np.array(prices)
        
        x = np.arange(len(prices_array))
        z = np.polyfit(x, prices_array, 1)
        slope = z[0]
        
        short_term = prices_array[-10:]  
        medium_term = prices_array[-30:]  
        
        short_change = (short_term[-1] - short_term[0]) / short_term[0]
        medium_change = (medium_term[-1] - medium_term[0]) / medium_term[0]
        
        score = 0.5
        trend_type = 'NEUTRAL'
        
        if slope > 0 and short_change > 0.02 and medium_change > 0:
            trend_type = 'UPTREND'
            score = 0.70
        elif slope < 0 and short_change < -0.02 and medium_change < 0:
            trend_type = 'DOWNTREND'
            score = 0.30
        elif slope > 0:
            trend_type = 'WEAK_UPTREND'
            score = 0.60
        elif slope < 0:
            trend_type = 'WEAK_DOWNTREND'
            score = 0.40
        
        return {
            'trend_type': trend_type,
            'score': score,
            'slope': float(slope),
            'short_term_change': float(short_change),
            'medium_term_change': float(medium_change),
        }
    
    @classmethod
    def _analyze_momentum(cls, prices: List[float]) -> Dict:
        """Analyze price momentum"""
        if len(prices) < 14:
            return {'momentum_type': 'NEUTRAL', 'score': 0.5}
        
        rsi = TechnicalAnalysisService.calculate_rsi(prices, period=14)
        
        score = 0.5
        momentum_type = 'NEUTRAL'
        
        if rsi > 70:
            momentum_type = 'STRONG_POSITIVE'
            score = 0.70
        elif rsi > 60:
            momentum_type = 'POSITIVE'
            score = 0.60
        elif rsi < 30:
            momentum_type = 'STRONG_NEGATIVE'
            score = 0.30
        elif rsi < 40:
            momentum_type = 'NEGATIVE'
            score = 0.40
        
        return {
            'momentum_type': momentum_type,
            'score': score,
            'rsi': float(rsi),
        }
    
    @classmethod
    def _analyze_volatility(cls, prices: List[float]) -> Dict:
        """Analyze price volatility"""
        if len(prices) < 20:
            return {'volatility_level': 'MODERATE', 'score': 0.5}
        
        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        volatility = np.std(returns) * 100
        
        score = 0.5
        volatility_level = 'MODERATE'
        
        if volatility > 3.0:
            volatility_level = 'HIGH'
            score = 0.45  
        elif volatility < 1.0:
            volatility_level = 'LOW'
            score = 0.55
        
        return {
            'volatility_level': volatility_level,
            'score': score,
            'volatility_percent': float(volatility),
        }
    
    @classmethod
    def _calculate_levels(
        cls,
        prices: List[float],
        highs: List[float],
        lows: List[float],
        technical_score: Dict,
        trend_score: Dict,
    ) -> Tuple[float, float]:
        """Calculate entry, target, and stop-loss levels"""
        current = prices[-1]
        
        period = 20
        resistance = max(highs[-period:])
        support = min(lows[-period:])
        atr = np.mean(np.array(highs[-period:]) - np.array(lows[-period:]))
        
        trend_strength = trend_score.get('score', 0.5)
        target_multiplier = 1.5 + (trend_strength * 1.0)
        target_price = current + (atr * target_multiplier)
        
        sl_multiplier = 0.5 + ((1 - trend_strength) * 0.5)
        stop_loss = current - (atr * sl_multiplier)
        
        stop_loss = max(stop_loss, support * 0.98)
        
        return target_price, stop_loss
    
    @classmethod
    def _calculate_confidence(
        cls,
        technical_score: Dict,
        volume_score: Dict,
        trend_score: Dict,
        momentum_score: Dict,
        volatility_score: Dict,
    ) -> float:
        """Calculate overall confidence"""
        weights = {
            'technical': 0.30,
            'volume': 0.20,
            'trend': 0.25,
            'momentum': 0.15,
            'volatility': 0.10,
        }
        
        confidence = (
            technical_score.get('score', 0.5) * weights['technical'] +
            volume_score.get('score', 0.5) * weights['volume'] +
            trend_score.get('score', 0.5) * weights['trend'] +
            momentum_score.get('score', 0.5) * weights['momentum'] +
            (1 - volatility_score.get('score', 0.5)) * weights['volatility']  # Inverse
        )
        
        return max(0.0, min(1.0, confidence))
    
    @classmethod
    def _get_signal_type(cls, confidence: float) -> str:
        """Convert confidence to signal type"""
        for signal_type, (min_conf, max_conf) in cls.SIGNAL_TYPES.items():
            if min_conf <= confidence <= max_conf:
                return signal_type
        return 'NEUTRAL'
    
    @classmethod
    def _calculate_probabilities(
        cls,
        technical_score: Dict,
        volume_score: Dict,
        trend_score: Dict,
    ) -> Dict:
        """Calculate specific probabilities"""
        uptrend_prob = trend_score.get('score', 0.5) * 1.2  
        uptrend_prob = max(0.0, min(1.0, uptrend_prob))
        
        breakout_prob = technical_score.get('score', 0.5) * volume_score.get('score', 0.5)
        breakout_prob = max(0.0, min(1.0, breakout_prob))
        
        support_hold_prob = 1.0 - (max(0.0, min(1.0, (1 - trend_score.get('score', 0.5)) * 0.8)))
        
        return {
            'uptrend_probability': float(uptrend_prob),
            'breakout_probability': float(breakout_prob),
            'support_hold_probability': float(support_hold_prob),
            'accuracy_disclaimer': 'These are calculated probabilities based on historical patterns, not guarantees',
        }
    
    @classmethod
    def _generate_warnings(
        cls,
        prices: List[float],
        volumes: List[int],
        confidence: float,
        risk_reward_ratio: float,
    ) -> List[str]:
        """Generate risk warnings"""
        warnings = []
        
        if confidence < 0.50:
            warnings.append('Low confidence signal - use smaller position size')
        
        if risk_reward_ratio < 1.5:
            warnings.append('Poor risk-reward ratio - target may not justify risk')
        
        if risk_reward_ratio > 5:
            warnings.append('Target too far away - may be unrealistic')
        
        if len(volumes) > 0:
            recent_vol = np.mean(volumes[-5:])
            if recent_vol < np.mean(volumes) * 0.7:
                warnings.append('Low volume - less reliable signal')
        
        if len(prices) > 20:
            prices_array = np.array(prices[-20:])
            returns = np.diff(prices_array) / prices_array[:-1]
            vol = np.std(returns)
            if vol > 0.03:
                warnings.append('High volatility - stop-loss may be hit prematurely')
        
        return warnings
    
    @classmethod
    def _generate_confidence_reason(cls, technical_score: Dict, volume_score: Dict, confidence: float) -> str:
        """Generate human-readable confidence reason"""
        factors = []
        
        patterns = technical_score.get('patterns', [])
        if patterns:
            factors.append(f"{len(patterns)} technical pattern(s) detected")
        
        volume_signal = volume_score.get('signal', 'NEUTRAL')
        if volume_signal != 'NEUTRAL':
            factors.append(f"{volume_signal.lower()} volume")
        
        if confidence > 0.75:
            strength = "Very strong"
        elif confidence > 0.60:
            strength = "Strong"
        elif confidence > 0.50:
            strength = "Moderate"
        else:
            strength = "Weak"
        
        return f"{strength} signals with {', '.join(factors) if factors else 'limited confirmation'}"
    
    @classmethod
    def _insufficient_data_signal(cls, symbol: str, current_price: float) -> Dict:
        """Return neutral signal when data is insufficient"""
        return {
            'symbol': symbol,
            'signal': 'NEUTRAL',
            'confidence': 0.40,
            'confidence_range': (0.40, 0.59),
            'entry_price': float(current_price),
            'target_price': float(current_price * 1.02),
            'stop_loss': float(current_price * 0.98),
            'risk_reward_ratio': 1.0,
            'factors': {},
            'warning_flags': ['Insufficient historical data for reliable analysis'],
            'probability_analysis': {},
            'timestamp': datetime.now().isoformat(),
            'data_quality': 'LOW',
            'confidence_reason': 'Not enough data points for analysis',
            'disclaimer': 'Wait for more data before trading',
        }
    
    @classmethod
    def _error_signal(cls, symbol: str, current_price: float, error: str) -> Dict:
        """Return error signal"""
        return {
            'symbol': symbol,
            'signal': 'NEUTRAL',
            'confidence': 0.0,
            'confidence_range': (0.0, 0.0),
            'entry_price': float(current_price),
            'target_price': None,
            'stop_loss': None,
            'risk_reward_ratio': 0,
            'factors': {},
            'warning_flags': [f'Error: {error}'],
            'probability_analysis': {},
            'timestamp': datetime.now().isoformat(),
            'data_quality': 'FAILED',
            'confidence_reason': 'Analysis failed',
            'error': error,
        }
