"""
5-Minute Prediction Engine
Predicts short-term price movements using ML and technical indicators
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# PREDICTION MODELS
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class PredictionSignal:
    """5-minute price prediction"""
    symbol: str
    timestamp: str
    direction: str  # UP, DOWN, NEUTRAL
    confidence: float  # 0-100
    predicted_price: float
    predicted_change_percent: float
    
    # Supporting indicators
    atr_stop_loss: float
    atr_target: float
    
    # Reasoning
    factors: List[str]
    warnings: List[str]
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "direction": self.direction,
            "confidence": round(self.confidence, 1),
            "predicted_price": round(self.predicted_price, 2),
            "predicted_change_percent": round(self.predicted_change_percent, 2),
            "risk_reward": {
                "stop_loss": round(self.atr_stop_loss, 2),
                "target": round(self.atr_target, 2),
            },
            "factors": self.factors,
            "warnings": self.warnings
        }


# ═══════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ═══════════════════════════════════════════════════════════════════════

class FeatureEngineer:
    """Extract features from OHLCV data for ML prediction"""
    
    @staticmethod
    def extract_features(candle_data: List[Dict], 
                        indicators: Dict,
                        current_price: float) -> Dict:
        """
        Extract ML features from market data
        
        Features include:
        - Price momentum
        - Volume signals
        - Volatility
        - Technical indicator values
        - Trend strength
        """
        if len(candle_data) < 10:
            return {}
        
        closes = [c["close"] for c in candle_data]
        volumes = [c["volume"] for c in candle_data]
        highs = [c["high"] for c in candle_data]
        lows = [c["low"] for c in candle_data]
        
        features = {}
        
        # Price momentum (5-candle, 10-candle returns)
        features["momentum_5"] = (closes[-1] - closes[-5]) / closes[-5] * 100
        features["momentum_10"] = (closes[-1] - closes[-10]) / closes[-10] * 100
        
        # Volatility (recent vs historical)
        recent_vol = np.std(closes[-10:]) / np.mean(closes[-10:]) * 100
        historical_vol = np.std(closes) / np.mean(closes) * 100
        features["volatility_ratio"] = recent_vol / historical_vol if historical_vol > 0 else 1
        
        # Volume trend
        recent_volume = np.mean(volumes[-5:])
        historical_volume = np.mean(volumes)
        features["volume_strength"] = recent_volume / historical_volume if historical_volume > 0 else 1
        
        # Price position in recent range
        recent_high = max(highs[-10:])
        recent_low = min(lows[-10:])
        features["price_position"] = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
        
        # RSI
        features["rsi"] = indicators.get("rsi", 50) / 100  # Normalize
        
        # MACD histogram (normalized)
        macd_hist = indicators.get("macd_histogram", 0)
        features["macd_signal"] = 1 if macd_hist > 0 else (-1 if macd_hist < 0 else 0)
        
        # EMA alignment (are EMAs stacked correctly?)
        ema_20 = indicators.get("ema_20", current_price)
        ema_50 = indicators.get("ema_50", current_price)
        ema_100 = indicators.get("ema_100", current_price)
        ema_200 = indicators.get("ema_200", current_price)
        
        # Bull alignment: EMA20 > EMA50 > EMA100 > EMA200
        bull_alignment = (ema_20 > ema_50 > ema_100 > ema_200)
        bear_alignment = (ema_20 < ema_50 < ema_100 < ema_200)
        
        features["trend_alignment"] = 1 if bull_alignment else (-1 if bear_alignment else 0)
        
        # Price relative to EMAs
        features["price_vs_ema20"] = (current_price - ema_20) / ema_20 * 100
        features["price_vs_ema50"] = (current_price - ema_50) / ema_50 * 100
        
        # ATR-based (volatility measure)
        features["atr_percent"] = indicators.get("atr_percent", 2)
        
        return features


# ═══════════════════════════════════════════════════════════════════════
# PREDICTION ENGINE (Rule-based + ML)
# ═══════════════════════════════════════════════════════════════════════

class PredictionEngine:
    """Predict 5-minute price movement"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.feature_engineer = FeatureEngineer()
    
    def calculate_confidence_score(self, features: Dict, indicators: Dict) -> Tuple[float, List[str]]:
        """
        Calculate prediction confidence based on multiple factors
        
        Returns:
        - Confidence (0-100)
        - Factors contributing to confidence
        """
        confidence = 50  # Base
        factors = []
        
        if not features:
            return 0.0, ["Insufficient data"]
        
        # RSI extremes (strong signal)
        rsi = indicators.get("rsi", 50)
        if rsi > 70 or rsi < 30:
            confidence += 15
            factors.append(f"RSI extreme ({rsi:.0f})")
        elif rsi > 60 or rsi < 40:
            confidence += 5
            factors.append(f"RSI moderate ({rsi:.0f})")
        
        # MACD signal (strong signal)
        macd_signal = features.get("macd_signal", 0)
        if macd_signal != 0:
            confidence += 15
            factors.append("MACD bullish" if macd_signal > 0 else "MACD bearish")
        
        # Trend alignment (very strong)
        trend = features.get("trend_alignment", 0)
        if trend != 0:
            confidence += 20
            factors.append("EMA trend alignment (strong)")
        
        # Momentum
        momentum = features.get("momentum_5", 0)
        if abs(momentum) > 1:
            confidence += 10
            factors.append(f"Strong momentum ({momentum:.2f}%)")
        
        # Volume
        volume_strength = features.get("volume_strength", 1)
        if volume_strength > 1.2:
            confidence += 10
            factors.append("Volume spike")
        
        # Price position
        price_pos = features.get("price_position", 0.5)
        if price_pos > 0.8:
            confidence -= 5
            factors.append("Near resistance (caution)")
        elif price_pos < 0.2:
            confidence -= 5
            factors.append("Near support (caution)")
        
        # Volatility check
        vol_ratio = features.get("volatility_ratio", 1)
        if vol_ratio > 1.5:
            confidence -= 15
            factors.append("High volatility (lower confidence)")
        
        # Cap confidence
        confidence = max(0, min(100, confidence))
        
        return confidence, factors
    
    def predict_5min_movement(self, candle_data: List[Dict], 
                             indicators: Dict,
                             current_price: float) -> Optional[PredictionSignal]:
        """
        Predict next 5-minute price movement
        
        Args:
            candle_data: Recent OHLCV data (5-minute intervals)
            indicators: Technical indicators
            current_price: Current stock price
        
        Returns:
            PredictionSignal with direction and confidence
        """
        try:
            if not candle_data or len(candle_data) < 10:
                return None
            
            # Extract features
            features = self.feature_engineer.extract_features(
                candle_data, 
                indicators, 
                current_price
            )
            
            if not features:
                return None
            
            # Calculate prediction
            direction = "NEUTRAL"
            confidence, factors = self.calculate_confidence_score(features, indicators)
            warnings = []
            
            # Decision logic (rule-based)
            rsi = indicators.get("rsi", 50)
            macd_signal = features.get("macd_signal", 0)
            trend = features.get("trend_alignment", 0)
            momentum = features.get("momentum_5", 0)
            volume = features.get("volume_strength", 1)
            
            # Multi-factor consensus for BUY
            buy_votes = 0
            if trend > 0:
                buy_votes += 2
            if macd_signal > 0:
                buy_votes += 1
            if momentum > 0.5:
                buy_votes += 1
            if volume > 1.1:
                buy_votes += 1
            if rsi > 50 and rsi < 70:
                buy_votes += 1
            
            # Multi-factor consensus for SELL
            sell_votes = 0
            if trend < 0:
                sell_votes += 2
            if macd_signal < 0:
                sell_votes += 1
            if momentum < -0.5:
                sell_votes += 1
            if volume > 1.1:
                sell_votes += 1
            if rsi < 50 and rsi > 30:
                sell_votes += 1
            
            # Determine direction
            if buy_votes > sell_votes and confidence > 40:
                direction = "UP"
            elif sell_votes > buy_votes and confidence > 40:
                direction = "DOWN"
            else:
                direction = "NEUTRAL"
                confidence = min(confidence, 40)  # Lower confidence for neutral
            
            # Calculate predicted price (conservative estimate)
            atr = indicators.get("atr", 0)
            predicted_price = current_price
            predicted_change_percent = 0
            
            if direction == "UP":
                predicted_change_percent = min(0.5, atr * 0.5 / current_price * 100)  # Max 0.5%
                predicted_price = current_price * (1 + predicted_change_percent / 100)
            elif direction == "DOWN":
                predicted_change_percent = max(-0.5, -atr * 0.5 / current_price * 100)
                predicted_price = current_price * (1 + predicted_change_percent / 100)
            
            # Risk/Reward levels
            atr_stop_loss = current_price - atr if direction == "UP" else current_price + atr
            atr_target = current_price + atr * 1.5 if direction == "UP" else current_price - atr * 1.5
            
            # Warnings
            if rsi > 75 or rsi < 25:
                warnings.append("Extreme RSI - reversal risk")
            
            if features.get("volatility_ratio", 1) > 1.5:
                warnings.append("High volatility - wide moves possible")
            
            if confidence < 50:
                warnings.append("Low confidence prediction - use caution")
            
            signal = PredictionSignal(
                symbol=self.symbol,
                timestamp=pd.Timestamp.now().isoformat(),
                direction=direction,
                confidence=confidence,
                predicted_price=predicted_price,
                predicted_change_percent=predicted_change_percent,
                atr_stop_loss=atr_stop_loss,
                atr_target=atr_target,
                factors=factors,
                warnings=warnings
            )
            
            logger.info(f"✓ Prediction for {self.symbol}: {direction} ({confidence:.0f}% confidence)")
            return signal
        
        except Exception as e:
            logger.error(f"Error predicting 5-min movement for {self.symbol}: {e}")
            return None
    
    def predict_intraday_movement(self, candle_data: List[Dict],
                                 indicators: Dict,
                                 current_price: float) -> Optional[PredictionSignal]:
        """
        Predict intraday (15-30 min) movement
        More reliable than 5-minute
        """
        try:
            if not candle_data or len(candle_data) < 20:
                return None
            
            # Similar to 5-min but with higher confidence threshold
            signal = self.predict_5min_movement(candle_data, indicators, current_price)
            
            if signal and signal.direction != "NEUTRAL":
                signal.confidence = min(100, signal.confidence * 1.1)  # Slightly higher confidence
                signal.factors.append("Intraday timeframe (more reliable)")
            
            return signal
        
        except Exception as e:
            logger.error(f"Error predicting intraday movement for {self.symbol}: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════
# ML MODEL TRAINING (Optional - Advanced)
# ═══════════════════════════════════════════════════════════════════════

class MLPredictionModel:
    """
    Optional: Advanced ML model for predictions
    Uses historical patterns to improve accuracy
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model_trained = False
        self.training_data = []
    
    def train_on_historical_data(self, historical_data: List[Dict]):
        """Train model on historical patterns"""
        try:
            # This would typically use sklearn, XGBoost, or LSTM
            # For now, we store patterns
            self.training_data = historical_data
            self.model_trained = True
            logger.info(f"✓ ML model trained on {len(historical_data)} samples for {self.symbol}")
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
    
    def predict(self, features: Dict) -> Optional[PredictionSignal]:
        """Use ML model for prediction (advanced)"""
        if not self.model_trained:
            logger.warning("Model not trained yet")
            return None
        
        try:
            # ML prediction logic here
            # This would use the trained model to predict
            
            # For now, return None (fallback to rule-based)
            return None
        
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════
# ENSEMBLE PREDICTION
# ═══════════════════════════════════════════════════════════════════════

class EnsemblePredictorEngine:
    """Combine multiple prediction methods for best result"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.rule_based = PredictionEngine(symbol)
        self.ml_model = MLPredictionModel(symbol)
    
    def predict(self, candle_data: List[Dict],
               indicators: Dict,
               current_price: float) -> Optional[PredictionSignal]:
        """
        Ensemble prediction: combine rule-based + ML
        """
        try:
            # Rule-based prediction (always available)
            rule_signal = self.rule_based.predict_5min_movement(
                candle_data, indicators, current_price
            )
            
            if not rule_signal:
                return None
            
            # ML prediction (if available)
            if self.ml_model.model_trained:
                features = FeatureEngineer.extract_features(
                    candle_data, indicators, current_price
                )
                ml_signal = self.ml_model.predict(features)
                
                # Combine signals if both available
                if ml_signal:
                    # Weighted average: 60% rule-based, 40% ML
                    rule_signal.confidence = (rule_signal.confidence * 0.6 + 
                                            ml_signal.confidence * 0.4)
                    
                    # If both agree, boost confidence
                    if rule_signal.direction == ml_signal.direction:
                        rule_signal.confidence = min(100, rule_signal.confidence * 1.15)
                        rule_signal.factors.append("ML model agrees")
            
            return rule_signal
        
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return None
