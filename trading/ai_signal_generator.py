
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .ai_formula_engine import (
    TrendFormulas, MomentumFormulas, VolatilityFormulas,
    VolumeFormulas, RiskFormulas, FormulaScoreCalculator, FormulaMeta
)
from .market_condition_detector import MarketConditionDetector, MarketAnalysis
from .trader_type_mapper import TraderTypeMapper, TraderType


class SignalType(Enum):
    """Trading signal types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    WEAK_BUY = "weak_buy"
    HOLD = "hold"
    WEAK_SELL = "weak_sell"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class AISignal:
    """AI-generated trading signal with full explanation"""
    signal: SignalType
    confidence: float
    
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: Optional[float]
    target_3: Optional[float]
    
    risk_reward_ratio: float
    position_size: int
    max_risk_amount: float
    
    formulas_used: List[str]
    formula_explanations: Dict[str, str]
    trader_type: str
    trader_suitability: str
    market_condition: str
    confidence_reason: str
    
    generated_at: str
    valid_until: str
    
    technical_indicators: Dict
    metadata: Dict


class SignalGenerator:
    """Generate AI-powered trading signals"""
    
    def __init__(self):
        self.market_detector = MarketConditionDetector()
        self.risk_manager = RiskFormulas()
    
    def generate_signal(self,
                       symbol: str,
                       current_price: float,
                       prices: List[float],
                       volumes: List[float],
                       highs: List[float],
                       lows: List[float],
                       trader_type: TraderType,
                       capital: float = 100000,
                       max_risk_percent: float = 1.0) -> AISignal:
        """Generate comprehensive AI signal"""
        
        market_analysis = self.market_detector.analyze_market(prices, volumes, highs, lows)
        
        trader_profile = TraderTypeMapper.get_profile(trader_type)
        
        indicators = self._calculate_indicators(prices, volumes, highs, lows)
        
        signal_type, confidence = self._determine_signal(
            market_analysis, indicators, trader_profile, current_price, prices
        )
        
        entry, sl, t1, t2, t3 = self._calculate_levels(
            current_price, signal_type, market_analysis, indicators
        )
        
        risk_reward, position_size, max_risk = self._calculate_risk_metrics(
            entry, sl, t1, capital, max_risk_percent
        )
        
        formulas_used = market_analysis.recommended_indicators
        explanations = self._generate_formula_explanations(
            formulas_used, indicators, trader_profile
        )
        
        signal = AISignal(
            signal=signal_type,
            confidence=confidence,
            entry_price=entry,
            stop_loss=sl,
            target_1=t1,
            target_2=t2,
            target_3=t3,
            risk_reward_ratio=risk_reward,
            position_size=position_size,
            max_risk_amount=max_risk,
            formulas_used=formulas_used,
            formula_explanations=explanations,
            trader_type=trader_type.value,
            trader_suitability=self._assess_trader_suitability(signal_type, market_analysis, trader_profile),
            market_condition=market_analysis.condition.value,
            confidence_reason=self._generate_confidence_reason(confidence, market_analysis, indicators),
            generated_at=datetime.now().isoformat(),
            valid_until=self._calculate_validity(trader_type),
            technical_indicators=self._format_indicators(indicators),
            metadata={
                "symbol": symbol,
                "market_analysis": {
                    "trend": market_analysis.trend,
                    "trend_strength": market_analysis.trend_strength.name,
                    "volatility_regime": market_analysis.volatility_regime.value,
                    "signal_quality": market_analysis.signal_quality,
                },
                "formulas": {k: v for k, v in FormulaMeta.FORMULA_INFO.items()}
            }
        )
        
        return signal
    
    def _calculate_indicators(self, prices: List[float], volumes: List[float],
                             highs: List[float], lows: List[float]) -> Dict:
        """Calculate all indicators"""
        
        return {
            "sma20": TrendFormulas.calculate_sma(prices, 20),
            "sma50": TrendFormulas.calculate_sma(prices, 50),
            "ema12": TrendFormulas.calculate_ema(prices, 12),
            "ema26": TrendFormulas.calculate_ema(prices, 26),
            "vwap": TrendFormulas.calculate_vwap(prices, volumes),
            
            
            "rsi": MomentumFormulas.calculate_rsi(prices, 14),
            "macd": MomentumFormulas.calculate_macd(prices),
            "roc": MomentumFormulas.calculate_roc(prices, 12),
            
        
            "bollinger_bands": VolatilityFormulas.calculate_bollinger_bands(prices, 20, 2.0),
            "atr": VolatilityFormulas.calculate_atr(highs, lows, prices, 14),
            
            "obv": VolumeFormulas.calculate_obv(prices, volumes),
            "volume_oscillator": VolumeFormulas.calculate_volume_oscillator(volumes),
            "current_volume": volumes[-1] if volumes else 0,
            "avg_volume": sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 0,
        }
    
    def _determine_signal(self, market_analysis: MarketAnalysis, indicators: Dict,
                         trader_profile, current_price: float, prices: List[float]) -> Tuple[SignalType, float]:
        """Determine signal type and confidence"""
        
        trend_score = market_analysis.trend_score
        momentum_score = market_analysis.momentum_score
        
        rsi = indicators["rsi"]
        macd, signal, histogram = indicators["macd"]
        
        buy_score = 0
        sell_score = 0
        
        if trend_score > 70:
            buy_score += 3
        elif trend_score < 30:
            sell_score += 3
        elif trend_score > 55:
            buy_score += 1.5
        elif trend_score < 45:
            sell_score += 1.5
        
        if rsi > 70:
            sell_score += 2
        elif rsi < 30:
            buy_score += 2
        elif rsi > 60:
            buy_score += 1
        elif rsi < 40:
            sell_score += 1
        
        if macd > signal:
            buy_score += 1.5
        else:
            sell_score += 1.5
        
        net_score = buy_score - sell_score
        
        if net_score > 5:
            signal_type = SignalType.STRONG_BUY
            confidence = 85
        elif net_score > 3:
            signal_type = SignalType.BUY
            confidence = 75
        elif net_score > 1:
            signal_type = SignalType.WEAK_BUY
            confidence = 65
        elif net_score > -1:
            signal_type = SignalType.HOLD
            confidence = 50
        elif net_score > -3:
            signal_type = SignalType.WEAK_SELL
            confidence = 65
        elif net_score > -5:
            signal_type = SignalType.SELL
            confidence = 75
        else:
            signal_type = SignalType.STRONG_SELL
            confidence = 85
        
        confidence = confidence * (market_analysis.signal_quality / 100)
        
        return signal_type, confidence
    
    def _calculate_levels(self, current_price: float, signal_type: SignalType,
                         market_analysis: MarketAnalysis, indicators: Dict) -> Tuple[float, float, float, Optional[float], Optional[float]]:
        """Calculate entry, stop-loss, and target prices"""
        
        atr = indicators["atr"]
        ema12 = indicators["ema12"]
        upper_bb, middle_bb, lower_bb = indicators["bollinger_bands"]
        
        if signal_type in [SignalType.STRONG_BUY, SignalType.BUY, SignalType.WEAK_BUY]:
            entry = current_price
            sl = current_price - (atr * 2)
            
            risk = entry - sl
            t1 = entry + risk * 1.0  
            t2 = entry + risk * 2.0  
            t3 = entry + risk * 3.0  
            
        else:  
      
            entry = current_price
            sl = current_price + (atr * 2)
            
            risk = sl - entry
            t1 = entry - risk * 1.0
            t2 = entry - risk * 2.0
            t3 = entry - risk * 3.0
        
        return entry, sl, t1, t2, t3
    
    def _calculate_risk_metrics(self, entry: float, sl: float, target: float,
                               capital: float, max_risk_percent: float) -> Tuple[float, int, float]:
        """Calculate risk metrics"""
        
        risk = abs(entry - sl)
        reward = abs(target - entry)
        risk_reward = reward / risk if risk > 0 else 0
        
        max_risk_amount = capital * (max_risk_percent / 100)
        position_size = int(max_risk_amount / risk) if risk > 0 else 0
        
        return risk_reward, position_size, max_risk_amount
    
    def _generate_formula_explanations(self, formulas_used: List[str],
                                      indicators: Dict, trader_profile) -> Dict[str, str]:
        """Generate explanations for each formula used"""
        
        explanations = {}
        
        for formula in formulas_used[:5]:  
            if formula == "EMA":
                ema12 = indicators["ema12"]
                ema26 = indicators["ema26"]
                if ema12 > ema26:
                    explanations[formula] = "EMA 12 is above EMA 26, confirming uptrend. Good for trend-following."
                else:
                    explanations[formula] = "EMA 12 is below EMA 26, showing downtrend."
            
            elif formula == "RSI":
                rsi = indicators["rsi"]
                if rsi > 70:
                    explanations[formula] = f"RSI at {rsi:.1f} indicates OVERBOUGHT conditions. Watch for reversal."
                elif rsi < 30:
                    explanations[formula] = f"RSI at {rsi:.1f} indicates OVERSOLD conditions. Potential bounce."
                else:
                    explanations[formula] = f"RSI at {rsi:.1f} in neutral zone."
            
            elif formula == "ATR":
                atr = indicators["atr"]
                explanations[formula] = f"ATR at {atr:.2f}. Use for setting stop-loss levels and position sizing."
            
            elif formula == "MACD":
                macd, signal, histogram = indicators["macd"]
                if histogram > 0:
                    explanations[formula] = "MACD histogram is positive and above signal line. Momentum is bullish."
                else:
                    explanations[formula] = "MACD histogram is negative. Momentum is bearish."
            
            elif formula == "VOLUME":
                vol_osc = indicators["volume_oscillator"]
                if vol_osc > 5:
                    explanations[formula] = "Volume oscillator positive. Strong volume supporting the move."
                else:
                    explanations[formula] = "Volume oscillator low. Watch for weak confirmation."
            
            elif formula == "OBV":
                obv = indicators["obv"]
                explanations[formula] = "On-Balance Volume shows cumulative volume trend."
            
            elif formula == "BOLLINGER_BANDS":
                upper, middle, lower = indicators["bollinger_bands"]
                explanations[formula] = "Bollinger Bands show volatility boundaries for range trading."
            
            elif formula == "VWAP":
                vwap = indicators["vwap"]
                explanations[formula] = "VWAP helps identify fair value price for intraday traders."
            
            else:
                explanations[formula] = FormulaMeta.FORMULA_INFO.get(formula, {}).get("description", "Formula applied")
        
        return explanations
    
    def _assess_trader_suitability(self, signal_type: SignalType,
                                  market_analysis: MarketAnalysis,
                                  trader_profile) -> str:
        """Assess suitability for this trader type"""
        
        if market_analysis.condition.value in trader_profile.ideal_market_conditions:
            return "IDEAL - Perfect market condition for this signal"
        elif "IDEAL" not in trader_profile.ideal_market_conditions:
            return "SUITABLE - Good market condition for this signal"
        else:
            return "CAUTION - Market condition may not be optimal for this trader type"
    
    def _generate_confidence_reason(self, confidence: float,
                                   market_analysis: MarketAnalysis,
                                   indicators: Dict) -> str:
        """Generate explanation for confidence level"""
        
        if confidence >= 85:
            return "Multiple indicators in strong agreement. High-quality signal with strong confirmation."
        elif confidence >= 70:
            return "Most indicators aligned. Good signal quality with solid confirmation."
        elif confidence >= 60:
            return "Mixed signals but trend is clear. Moderate confidence level."
        elif confidence >= 50:
            return "Conflicting signals. Proceed with caution."
        else:
            return "Weak signal. Wait for better confirmation before acting."
    
    def _calculate_validity(self, trader_type: TraderType) -> str:
        """Calculate validity period based on trader type"""
        
        validity_map = {
            TraderType.INTRADAY: "Valid for 4 hours",
            TraderType.SWING: "Valid for 5 days",
            TraderType.POSITIONAL: "Valid for 2 weeks",
            TraderType.LONG_TERM: "Valid for 3 months",
            TraderType.OPTIONS: "Valid for 3 days",
            TraderType.AI_ALGO: "Valid for 8 hours",
            TraderType.INVESTOR: "Valid for 6 months",
        }
        
        return validity_map.get(trader_type, "Valid for 24 hours")
    
    def _format_indicators(self, indicators: Dict) -> Dict:
        """Format indicators for output"""
        
        macd, signal, histogram = indicators["macd"]
        upper_bb, middle_bb, lower_bb = indicators["bollinger_bands"]
        
        return {
            "trend": {
                "sma20": round(indicators["sma20"], 2),
                "sma50": round(indicators["sma50"], 2),
                "ema12": round(indicators["ema12"], 2),
                "ema26": round(indicators["ema26"], 2),
                "vwap": round(indicators["vwap"], 2),
            },
            "momentum": {
                "rsi": round(indicators["rsi"], 2),
                "macd": round(macd, 4),
                "macd_signal": round(signal, 4),
                "macd_histogram": round(histogram, 4),
                "roc": round(indicators["roc"], 2),
            },
            "volatility": {
                "atr": round(indicators["atr"], 2),
                "bb_upper": round(upper_bb, 2),
                "bb_middle": round(middle_bb, 2),
                "bb_lower": round(lower_bb, 2),
                "bb_width": round(upper_bb - lower_bb, 2),
            },
            "volume": {
                "obv": round(indicators["obv"], 0),
                "volume_oscillator": round(indicators["volume_oscillator"], 2),
                "current_volume": indicators["current_volume"],
                "avg_volume": round(indicators["avg_volume"], 0),
            }
        }
