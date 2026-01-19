"""
Signal Generation Pipeline
Combines data, indicators, and predictions into actionable trading signals
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from trading.data_integration import DataIntegrationEngine, is_market_open
from trading.technical_indicators import TechnicalIndicatorsEngine, PatternDetectionEngine
from trading.prediction_engine import PredictionEngine, EnsemblePredictorEngine

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# SIGNAL MODELS
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class TradingSignal:
    """Complete trading signal for user"""
    symbol: str
    timestamp: str
    
    # Signal
    signal_type: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    
    # Execution levels
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: Optional[float]
    
    # Risk
    risk_reward_ratio: float
    position_size_percent: float  # % of capital
    
    # Market context
    market_status: str  # LIVE, DELAYED, HISTORICAL
    data_freshness_minutes: int
    
    # Sources
    data_sources: List[str]
    indicator_consensus: Dict
    pattern_signals: List[str]
    prediction_signal: Optional[Dict]
    
    # Metadata
    is_executable: bool
    reasons: List[str]
    warnings: List[str]
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "signal": {
                "type": self.signal_type,
                "confidence": round(self.confidence, 1),
                "is_executable": self.is_executable,
            },
            "execution": {
                "entry": round(self.entry_price, 2),
                "stop_loss": round(self.stop_loss, 2),
                "target_1": round(self.target_1, 2),
                "target_2": round(self.target_2, 2),
                "target_3": round(self.target_3, 2) if self.target_3 else None,
            },
            "risk": {
                "risk_reward_ratio": round(self.risk_reward_ratio, 2),
                "position_size_percent": round(self.position_size_percent, 2),
            },
            "market": {
                "status": self.market_status,
                "data_freshness_minutes": self.data_freshness_minutes,
            },
            "analysis": {
                "data_sources": self.data_sources,
                "indicator_consensus": self.indicator_consensus,
                "patterns": self.pattern_signals,
                "prediction": self.prediction_signal,
            },
            "metadata": {
                "reasons": self.reasons,
                "warnings": self.warnings,
            }
        }


# ═══════════════════════════════════════════════════════════════════════
# SIGNAL GENERATION ENGINE
# ═══════════════════════════════════════════════════════════════════════

class SignalGenerationEngine:
    """Generate trading signals from market data"""
    
    def __init__(self, symbol: str, capital: float = 100000):
        self.symbol = symbol
        self.capital = capital
        
        self.data_engine = DataIntegrationEngine()
        self.indicators_engine = TechnicalIndicatorsEngine(symbol)
        self.pattern_engine = PatternDetectionEngine(symbol)
        self.prediction_engine = EnsemblePredictorEngine(symbol)
    
    def generate_live_signal(self) -> Optional[Dict]:
        """
        Generate live trading signal with current market data
        Complete end-to-end pipeline
        """
        try:
            logger.info(f"Generating live signal for {self.symbol}...")
            
            # 1. Get market data
            market_data = self.data_engine.get_complete_market_data(self.symbol)
            
            if not market_data.get("quote"):
                return {
                    "status": "ERROR",
                    "message": "Could not fetch market data",
                    "symbol": self.symbol
                }
            
            current_price = market_data["quote"]["price"]
            
            # 2. Validate data quality
            data_quality = self.data_engine.validate_data_quality(self.symbol, market_data)
            
            if not data_quality["is_valid"]:
                return {
                    "status": "INSUFFICIENT_DATA",
                    "message": f"Data quality issues: {', '.join(data_quality['issues'])}",
                    "symbol": self.symbol,
                    "data_quality": data_quality
                }
            
            # 3. Calculate indicators
            daily_candles = market_data.get("historical", {}).get("candles", [])
            if not daily_candles:
                daily_candles = []
            
            daily_candles_dict = [
                {
                    "open": c["open"],
                    "high": c["high"],
                    "low": c["low"],
                    "close": c["close"],
                    "volume": c["volume"]
                }
                for c in daily_candles[-100:]  # Last 100 daily candles
            ]
            
            indicators = self.indicators_engine.calculate_all(daily_candles_dict)
            if not indicators:
                return {
                    "status": "ERROR",
                    "message": "Could not calculate indicators",
                    "symbol": self.symbol
                }
            
            indicators_dict = indicators.to_dict()
            
            # 4. Detect patterns
            patterns = self.pattern_engine.detect_all_patterns(daily_candles_dict)
            
            # 5. Generate prediction (5-min and intraday)
            intraday_candles = market_data.get("intraday", {}).get("candles", [])
            intraday_candles_dict = [
                {
                    "open": c["open"],
                    "high": c["high"],
                    "low": c["low"],
                    "close": c["close"],
                    "volume": c["volume"]
                }
                for c in intraday_candles[-50:]  # Last 50 5-min candles
            ]
            
            prediction_signal = None
            if intraday_candles_dict:
                prediction = self.prediction_engine.predict(
                    intraday_candles_dict,
                    indicators_dict,
                    current_price
                )
                if prediction:
                    prediction_signal = prediction.to_dict()
            
            # 6. Generate signal
            signal = self._generate_signal_from_components(
                current_price=current_price,
                indicators=indicators,
                indicators_dict=indicators_dict,
                patterns=patterns,
                prediction=prediction_signal,
                market_data=market_data
            )
            
            logger.info(f"✓ Signal generated for {self.symbol}: {signal.signal_type} ({signal.confidence:.0f}%)")
            return signal.to_dict()
        
        except Exception as e:
            logger.error(f"Error generating signal for {self.symbol}: {e}")
            return {
                "status": "ERROR",
                "message": str(e),
                "symbol": self.symbol
            }
    
    def _generate_signal_from_components(self, current_price: float,
                                        indicators,
                                        indicators_dict: Dict,
                                        patterns: Dict,
                                        prediction: Optional[Dict],
                                        market_data: Dict) -> TradingSignal:
        """
        Internal method to generate signal from all components
        """
        # Market status
        market_open = is_market_open()
        data_sources = market_data.get("quote", {}).get("source", "UNKNOWN")
        
        # Determine signal type
        signal_type = self._determine_signal_type(indicators_dict, prediction, patterns)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            signal_type, indicators_dict, prediction, patterns
        )
        
        # Calculate levels
        atr = indicators_dict["volatility"]["atr"]
        
        if signal_type == "BUY":
            entry_price = current_price
            stop_loss = entry_price - atr * 2
            target_1 = entry_price + atr * 2
            target_2 = entry_price + atr * 3.5
            target_3 = entry_price + atr * 5
        elif signal_type == "SELL":
            entry_price = current_price
            stop_loss = entry_price + atr * 2
            target_1 = entry_price - atr * 2
            target_2 = entry_price - atr * 3.5
            target_3 = entry_price - atr * 5
        else:  # HOLD
            entry_price = current_price
            stop_loss = entry_price - atr * 1
            target_1 = entry_price + atr * 1
            target_2 = entry_price + atr * 2
            target_3 = None
        
        # Risk/Reward
        if signal_type != "HOLD":
            risk = abs(entry_price - stop_loss)
            reward = abs(target_2 - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
        else:
            risk_reward_ratio = 0
        
        # Position size (2% risk per trade)
        risk_amount = self.capital * 0.02
        position_size = risk_amount / abs(entry_price - stop_loss) if entry_price != stop_loss else 0
        position_size_percent = (position_size * entry_price / self.capital * 100) if self.capital > 0 else 0
        
        # Data freshness
        quote_timestamp = market_data.get("quote", {}).get("timestamp", datetime.now().isoformat())
        quote_time = datetime.fromisoformat(quote_timestamp)
        data_freshness = int((datetime.now() - quote_time).total_seconds() / 60)
        
        # Determine executability
        is_executable = (
            signal_type != "HOLD" and
            confidence >= 50 and
            market_open and
            risk_reward_ratio >= 1.5 and
            position_size_percent > 0
        )
        
        # Reasons
        reasons = [
            f"Indicator consensus: {signal_type}",
            f"ATR: {atr:.2f}",
            f"Risk/Reward: 1:{risk_reward_ratio:.1f}",
        ]
        
        if prediction:
            reasons.append(f"5-min prediction: {prediction.get('direction')} ({prediction.get('confidence'):.0f}%)")
        
        # Warnings
        warnings = []
        
        if confidence < 60:
            warnings.append("Low confidence - use caution")
        
        if not market_open:
            warnings.append("Market is closed - signal is historical")
        
        if data_freshness > 5:
            warnings.append(f"Data is {data_freshness} minutes old")
        
        if risk_reward_ratio < 2:
            warnings.append("Risk/Reward ratio below 1:2 target")
        
        indicator_consensus = {
            "ema_trend": "BULLISH" if indicators_dict["trend"]["ema_20"] > indicators_dict["trend"]["ema_50"] else "BEARISH",
            "rsi": indicators_dict["momentum"]["rsi_signal"],
            "macd": indicators_dict["momentum"]["macd_signal"],
            "volume": indicators_dict["volume"]["volume_trend"],
        }
        
        pattern_signals = patterns.get("patterns", [])
        
        signal = TradingSignal(
            symbol=self.symbol,
            timestamp=datetime.now().isoformat(),
            signal_type=signal_type,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            target_3=target_3,
            risk_reward_ratio=risk_reward_ratio,
            position_size_percent=position_size_percent,
            market_status="LIVE" if market_open else "HISTORICAL",
            data_freshness_minutes=data_freshness,
            data_sources=[data_sources],
            indicator_consensus=indicator_consensus,
            pattern_signals=pattern_signals,
            prediction_signal=prediction,
            is_executable=is_executable,
            reasons=reasons,
            warnings=warnings
        )
        
        return signal
    
    def _determine_signal_type(self, indicators: Dict, prediction: Optional[Dict],
                              patterns: Dict) -> str:
        """Determine BUY, SELL, or HOLD"""
        
        # Count signals
        buy_signals = 0
        sell_signals = 0
        
        # EMA signals
        ema_20 = indicators["trend"]["ema_20"]
        ema_50 = indicators["trend"]["ema_50"]
        ema_100 = indicators["trend"]["ema_100"]
        ema_200 = indicators["trend"]["ema_200"]
        
        if ema_20 > ema_50 > ema_100 > ema_200:
            buy_signals += 2
        elif ema_20 < ema_50 < ema_100 < ema_200:
            sell_signals += 2
        
        # RSI signals
        if indicators["momentum"]["rsi_signal"] == "OVERBOUGHT":
            sell_signals += 1
        elif indicators["momentum"]["rsi_signal"] == "OVERSOLD":
            buy_signals += 1
        
        # MACD signals
        if indicators["momentum"]["macd_signal"] == "BULLISH":
            buy_signals += 1
        elif indicators["momentum"]["macd_signal"] == "BEARISH":
            sell_signals += 1
        
        # Pattern signals
        patterns_list = patterns.get("patterns", [])
        if "double_bottom" in patterns_list or "uptrend" in patterns_list:
            buy_signals += 1
        if "double_top" in patterns_list or "downtrend" in patterns_list:
            sell_signals += 1
        
        # Prediction signals
        if prediction:
            if prediction["direction"] == "UP":
                buy_signals += 1
            elif prediction["direction"] == "DOWN":
                sell_signals += 1
        
        # Determine signal
        if buy_signals > sell_signals + 1:
            return "BUY"
        elif sell_signals > buy_signals + 1:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_confidence(self, signal_type: str, indicators: Dict,
                             prediction: Optional[Dict], patterns: Dict) -> float:
        """Calculate confidence score"""
        confidence = 50
        
        if signal_type == "HOLD":
            return 0.0
        
        # Indicator strength
        rsi = indicators["momentum"]["rsi"]
        if signal_type == "BUY":
            if rsi < 70:  # Not overbought
                confidence += 15
            if indicators["trend"]["ema_20"] > indicators["trend"]["ema_50"]:
                confidence += 15
            if indicators["momentum"]["macd_signal"] == "BULLISH":
                confidence += 10
        else:  # SELL
            if rsi > 30:  # Not oversold
                confidence += 15
            if indicators["trend"]["ema_20"] < indicators["trend"]["ema_50"]:
                confidence += 15
            if indicators["momentum"]["macd_signal"] == "BEARISH":
                confidence += 10
        
        # Volume confirmation
        if indicators["volume"]["volume_trend"] == "INCREASING":
            confidence += 5
        
        # Pattern confirmation
        patterns_list = patterns.get("patterns", [])
        if patterns_list:
            confidence += 5
        
        # Prediction agreement
        if prediction and prediction["direction"] != "NEUTRAL":
            confidence += 5
        
        # Cap confidence
        return min(100, confidence)


# ═══════════════════════════════════════════════════════════════════════
# SIGNAL MONITOR
# ═══════════════════════════════════════════════════════════════════════

class SignalMonitor:
    """Monitor active signals and update them"""
    
    def __init__(self):
        self.active_signals: Dict[str, Dict] = {}
        self.signal_engines: Dict[str, SignalGenerationEngine] = {}
    
    def add_signal_watch(self, symbol: str, capital: float = 100000):
        """Start monitoring a symbol"""
        self.signal_engines[symbol] = SignalGenerationEngine(symbol, capital)
        logger.info(f"Started monitoring {symbol}")
    
    def get_updated_signal(self, symbol: str) -> Optional[Dict]:
        """Get fresh signal for symbol"""
        if symbol not in self.signal_engines:
            self.add_signal_watch(symbol)
        
        return self.signal_engines[symbol].generate_live_signal()
    
    def refresh_all_signals(self) -> Dict[str, Dict]:
        """Refresh all monitored signals"""
        updated = {}
        
        for symbol, engine in self.signal_engines.items():
            signal = engine.generate_live_signal()
            if signal:
                updated[symbol] = signal
        
        return updated


# ═══════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════

_signal_monitor = None


def get_signal_monitor() -> SignalMonitor:
    """Get singleton signal monitor"""
    global _signal_monitor
    if _signal_monitor is None:
        _signal_monitor = SignalMonitor()
    return _signal_monitor
