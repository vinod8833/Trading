"""
Market Condition Detector
Analyzes market conditions to recommend appropriate indicators
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from .ai_formula_engine import (
    TrendFormulas, MomentumFormulas, VolatilityFormulas,
    VolumeFormulas, AIMetrics, FormulaScoreCalculator
)


class MarketCondition(Enum):
    """Market condition states"""
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    WEAK_UPTREND = "weak_uptrend"
    NEUTRAL = "neutral"
    RANGE_BOUND = "range_bound"
    WEAK_DOWNTREND = "weak_downtrend"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"
    BREAKOUT = "breakout"
    BREAKOUT_DOWN = "breakout_down"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


class VolatilityRegime(Enum):
    """Volatility regimes"""
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrendStrength(Enum):
    """Trend strength levels"""
    VERY_WEAK = 0
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4


@dataclass
class MarketAnalysis:
    """Complete market analysis result"""
    condition: MarketCondition
    trend: str
    trend_strength: TrendStrength
    volatility_regime: VolatilityRegime
    trend_score: float
    momentum_score: float
    volatility_score: float
    volume_strength: float
    
    # Market parameters
    current_price: float
    sma20: float
    sma50: float
    ema12: float
    ema26: float
    rsi: float
    atr: float
    upper_bb: float
    lower_bb: float
    
    # Recommendations
    recommended_indicators: List[str]
    signal_quality: float
    confidence_level: float
    explanation: str


class MarketConditionDetector:
    """Detect market conditions and recommend indicators"""
    
    def __init__(self):
        self.min_data_points = 50
    
    def analyze_market(self, prices: List[float], volumes: List[float],
                      highs: List[float], lows: List[float]) -> MarketAnalysis:
        """Complete market analysis"""
        
        if len(prices) < self.min_data_points:
            return self._insufficient_data_response()
        
        # Calculate all indicators
        sma20 = TrendFormulas.calculate_sma(prices, 20)
        sma50 = TrendFormulas.calculate_sma(prices, 50)
        ema12 = TrendFormulas.calculate_ema(prices, 12)
        ema26 = TrendFormulas.calculate_ema(prices, 26)
        
        current_price = prices[-1]
        rsi = MomentumFormulas.calculate_rsi(prices, 14)
        macd, signal, histogram = MomentumFormulas.calculate_macd(prices)
        roc = MomentumFormulas.calculate_roc(prices, 12)
        
        upper_bb, middle_bb, lower_bb = VolatilityFormulas.calculate_bollinger_bands(prices, 20, 2.0)
        atr = VolatilityFormulas.calculate_atr(highs, lows, prices, 14)
        
        obv = VolumeFormulas.calculate_obv(prices, volumes)
        vol_osc = VolumeFormulas.calculate_volume_oscillator(volumes)
        
        # Calculate scores
        trend = TrendFormulas.get_trend(current_price, sma20, sma50, ema12, ema26)
        trend_score = FormulaScoreCalculator.calculate_trend_score(
            trend, current_price, sma20, sma50, ema12, ema26
        )
        momentum_score = FormulaScoreCalculator.calculate_momentum_score(rsi, macd, signal, roc)
        volatility_score = FormulaScoreCalculator.calculate_volatility_score(
            upper_bb, lower_bb, current_price, atr, atr
        )
        volume_strength = FormulaScoreCalculator.calculate_volume_strength(
            obv, vol_osc, volumes[-1], sum(volumes[-20:]) / 20
        )
        
        # Determine market condition
        condition, trend_strength = self._determine_condition(
            trend_score, momentum_score, volatility_score, rsi, current_price,
            upper_bb, lower_bb, sma20, sma50
        )
        
        # Determine volatility regime
        volatility_regime = self._determine_volatility_regime(atr, prices)
        
        # Get recommended indicators
        recommended = self._recommend_indicators(condition, volatility_regime, rsi)
        
        # Calculate confidence
        confidence = self._calculate_confidence(trend_score, momentum_score, volume_strength)
        
        # Generate explanation
        explanation = self._generate_explanation(
            condition, trend, trend_strength, recommended, confidence
        )
        
        return MarketAnalysis(
            condition=condition,
            trend=trend,
            trend_strength=trend_strength,
            volatility_regime=volatility_regime,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
            volume_strength=volume_strength,
            current_price=current_price,
            sma20=sma20,
            sma50=sma50,
            ema12=ema12,
            ema26=ema26,
            rsi=rsi,
            atr=atr,
            upper_bb=upper_bb,
            lower_bb=lower_bb,
            recommended_indicators=recommended,
            signal_quality=confidence,
            confidence_level=confidence,
            explanation=explanation
        )
    
    def _determine_condition(self, trend_score: float, momentum_score: float,
                            volatility_score: float, rsi: float, current_price: float,
                            upper_bb: float, lower_bb: float,
                            sma20: float, sma50: float) -> Tuple[MarketCondition, TrendStrength]:
        """Determine market condition"""
        
        # Determine base trend strength
        if trend_score > 80:
            trend_strength = TrendStrength.VERY_STRONG
        elif trend_score > 65:
            trend_strength = TrendStrength.STRONG
        elif trend_score > 55:
            trend_strength = TrendStrength.MODERATE
        elif trend_score > 40:
            trend_strength = TrendStrength.WEAK
        else:
            trend_strength = TrendStrength.VERY_WEAK
        
        # Check for breakout
        if current_price > upper_bb and trend_score > 70:
            return MarketCondition.BREAKOUT, trend_strength
        elif current_price < lower_bb and trend_score < 30:
            return MarketCondition.BREAKOUT_DOWN, trend_strength
        
        # Check for volatility
        if volatility_score > 75:
            return MarketCondition.HIGH_VOLATILITY, trend_strength
        elif volatility_score < 25:
            return MarketCondition.LOW_VOLATILITY, trend_strength
        
        # Check for range
        if 40 <= volatility_score <= 60 and abs(momentum_score - 50) < 15:
            return MarketCondition.RANGE_BOUND, trend_strength
        
        # Check for trend
        if trend_score > 70:
            if trend_score > 80:
                return MarketCondition.STRONG_UPTREND, trend_strength
            else:
                return MarketCondition.UPTREND, trend_strength
        elif trend_score > 55:
            return MarketCondition.WEAK_UPTREND, trend_strength
        elif trend_score < 30:
            if trend_score < 20:
                return MarketCondition.STRONG_DOWNTREND, trend_strength
            else:
                return MarketCondition.DOWNTREND, trend_strength
        elif trend_score < 45:
            return MarketCondition.WEAK_DOWNTREND, trend_strength
        else:
            return MarketCondition.NEUTRAL, trend_strength
    
    def _determine_volatility_regime(self, atr: float, prices: List[float]) -> VolatilityRegime:
        """Determine volatility regime"""
        
        # Calculate historical ATR ranges
        avg_price = sum(prices[-50:]) / 50 if len(prices) >= 50 else prices[-1]
        atr_percent = (atr / avg_price * 100) if avg_price > 0 else 0
        
        if atr_percent < 0.5:
            return VolatilityRegime.VERY_LOW
        elif atr_percent < 1.0:
            return VolatilityRegime.LOW
        elif atr_percent < 2.0:
            return VolatilityRegime.NORMAL
        elif atr_percent < 3.0:
            return VolatilityRegime.HIGH
        else:
            return VolatilityRegime.VERY_HIGH
    
    def _recommend_indicators(self, condition: MarketCondition,
                             volatility_regime: VolatilityRegime,
                             rsi: float) -> List[str]:
        """Recommend indicators based on market condition"""
        
        recommendations = {}
        
        # Trend recommendations
        if condition in [MarketCondition.STRONG_UPTREND, MarketCondition.UPTREND,
                         MarketCondition.WEAK_UPTREND, MarketCondition.DOWNTREND,
                         MarketCondition.STRONG_DOWNTREND]:
            recommendations["trend"] = ["EMA", "SMA", "VWAP"]
        
        # Momentum recommendations
        if condition in [MarketCondition.RANGE_BOUND]:
            recommendations["momentum"] = ["RSI", "MACD", "ROC"]
        
        # Volatility recommendations
        if volatility_regime in [VolatilityRegime.VERY_HIGH, VolatilityRegime.HIGH]:
            recommendations["volatility"] = ["ATR", "BOLLINGER_BANDS"]
        
        # Volume recommendations
        recommendations["volume"] = ["OBV", "VOLUME"]
        
        # Flatten and prioritize
        all_recs = []
        
        # High priority
        if "trend" in recommendations:
            all_recs.extend(recommendations.get("trend", []))
        
        # Medium priority
        if "momentum" in recommendations:
            all_recs.extend(recommendations.get("momentum", []))
        elif condition == MarketCondition.RANGE_BOUND:
            all_recs.extend(["RSI", "MACD"])
        else:
            all_recs.append("RSI")
        
        # Add volatility
        all_recs.extend(recommendations.get("volatility", ["ATR"]))
        
        # Add volume
        all_recs.extend(recommendations.get("volume", []))
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for item in all_recs:
            if item not in seen:
                seen.add(item)
                result.append(item)
        
        return result[:6]  # Return top 6
    
    def _calculate_confidence(self, trend_score: float, momentum_score: float,
                             volume_strength: float) -> float:
        """Calculate signal confidence (0-100)"""
        
        # Average the scores
        confidence = (trend_score * 0.4 + momentum_score * 0.3 + volume_strength * 0.3)
        
        # Adjust for alignment
        alignment = abs(trend_score - momentum_score)
        if alignment < 10:
            confidence += 5  # Good alignment
        elif alignment > 30:
            confidence -= 10  # Poor alignment
        
        return max(0, min(confidence, 100))
    
    def _generate_explanation(self, condition: MarketCondition,
                             trend: str, trend_strength: TrendStrength,
                             recommendations: List[str],
                             confidence: float) -> str:
        """Generate human-readable explanation"""
        
        explanations = {
            MarketCondition.STRONG_UPTREND: "Strong uptrend detected. Use trend-following indicators like EMA, VWAP, and SMA.",
            MarketCondition.UPTREND: "Uptrend in place. Follow the trend with EMA or SMA. Watch RSI for overbought conditions.",
            MarketCondition.WEAK_UPTREND: "Weak uptrend. Wait for confirmation from volume or momentum before entering.",
            MarketCondition.NEUTRAL: "Neutral market. Use range-based trading with RSI and Bollinger Bands.",
            MarketCondition.RANGE_BOUND: "Range-bound market. Trade the extremes using RSI (overbought/oversold) and Bollinger Bands.",
            MarketCondition.WEAK_DOWNTREND: "Weak downtrend. Wait for confirmation before shorting.",
            MarketCondition.DOWNTREND: "Downtrend in place. Short-term traders can sell on bounces.",
            MarketCondition.STRONG_DOWNTREND: "Strong downtrend. Avoid long positions. Consider short trades with proper risk management.",
            MarketCondition.BREAKOUT: "Breakout upward detected. Use breakout strategies with ATR for stop loss.",
            MarketCondition.BREAKOUT_DOWN: "Breakout downward detected. Short traders should act. Long traders should exit.",
            MarketCondition.HIGH_VOLATILITY: "High volatility environment. Use wider stops. Focus on ATR for position sizing.",
            MarketCondition.LOW_VOLATILITY: "Low volatility. Expect a breakout soon. Position size accordingly.",
        }
        
        base_explanation = explanations.get(condition, "Market analysis in progress.")
        confidence_text = f" (Confidence: {confidence:.0f}%)"
        
        return base_explanation + confidence_text
    
    def _insufficient_data_response(self) -> MarketAnalysis:
        """Return default response when insufficient data"""
        return MarketAnalysis(
            condition=MarketCondition.NEUTRAL,
            trend="NEUTRAL",
            trend_strength=TrendStrength.VERY_WEAK,
            volatility_regime=VolatilityRegime.NORMAL,
            trend_score=50,
            momentum_score=50,
            volatility_score=50,
            volume_strength=50,
            current_price=0,
            sma20=0,
            sma50=0,
            ema12=0,
            ema26=0,
            rsi=50,
            atr=0,
            upper_bb=0,
            lower_bb=0,
            recommended_indicators=["SMA", "EMA", "RSI", "ATR"],
            signal_quality=0,
            confidence_level=0,
            explanation="Insufficient data for market analysis. Please provide at least 50 data points."
        )
