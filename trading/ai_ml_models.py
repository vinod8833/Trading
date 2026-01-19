import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from typing import Dict, Tuple, Optional
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class PricePredictionModel:
    """Machine Learning models for stock price prediction"""
    
    @staticmethod
    def prepare_features(data: pd.DataFrame, lookback: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for ML model
        Uses technical indicators and price history
        """
        features = []
        targets = []
        
        for i in range(lookback, len(data) - 1):
            window = data.iloc[i-lookback:i]
            
            returns = window['Close'].pct_change().values
            volatility = np.std(returns)
            
            delta = window['Close'].diff()
            gain = np.mean(np.maximum(delta, 0))
            loss = np.mean(np.maximum(-delta, 0))
            rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            
            sma_ratio = window['Close'].iloc[-1] / (np.mean(window['Close']) + 1e-10)
            
            volume_change = window['Volume'].iloc[-1] / (np.mean(window['Volume']) + 1e-10)
            
            feature_vector = [
                volatility,
                rsi,
                sma_ratio,
                volume_change,
                returns[-1] if len(returns) > 0 else 0,
                np.max(returns) if len(returns) > 0 else 0,
            ]
            
            features.append(feature_vector)
            targets.append(data['Close'].iloc[i+1] / data['Close'].iloc[i] - 1)  
        
        return np.array(features), np.array(targets)
    
    @staticmethod
    def train_ensemble_model(data: pd.DataFrame, lookback: int = 20):
        """Train ensemble model combining multiple algorithms"""
        try:
            if len(data) < lookback + 10:
                logger.warning("Insufficient data for model training")
                return None
            
            X, y = PricePredictionModel.prepare_features(data, lookback)
            
            if len(X) < 10:
                return None
            
            rf_model = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            rf_model.fit(X, y)
            
            gb_model = GradientBoostingRegressor(
                n_estimators=50,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            gb_model.fit(X, y)
            
            lr_model = LinearRegression()
            lr_model.fit(X, y)
            
            return {
                'rf': rf_model,
                'gb': gb_model,
                'lr': lr_model,
                'X_shape': X.shape,
            }
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return None
    
    @staticmethod
    def predict_next_day(data: pd.DataFrame, models: Dict, lookback: int = 20) -> Optional[Dict]:
        """Predict next day price movement"""
        try:
            if models is None or len(data) < lookback:
                return None
            
            window = data.iloc[-lookback:]
            returns = window['Close'].pct_change().values
            volatility = np.std(returns)
            
            delta = window['Close'].diff()
            gain = np.mean(np.maximum(delta, 0))
            loss = np.mean(np.maximum(-delta, 0))
            rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            
            sma_ratio = window['Close'].iloc[-1] / (np.mean(window['Close']) + 1e-10)
            volume_change = window['Volume'].iloc[-1] / (np.mean(window['Volume']) + 1e-10)
            
            X = np.array([[
                volatility,
                rsi,
                sma_ratio,
                volume_change,
                returns[-1] if len(returns) > 0 else 0,
                np.max(returns) if len(returns) > 0 else 0,
            ]])
            
            rf_pred = models['rf'].predict(X)[0]
            gb_pred = models['gb'].predict(X)[0]
            lr_pred = models['lr'].predict(X)[0]
            
            ensemble_pred = (rf_pred * 0.5 + gb_pred * 0.4 + lr_pred * 0.1)
            
            current_price = data['Close'].iloc[-1]
            
            return {
                'rf_return': float(rf_pred),
                'gb_return': float(gb_pred),
                'lr_return': float(lr_pred),
                'ensemble_return': float(ensemble_pred),
                'predicted_price': float(current_price * (1 + ensemble_pred)),
                'current_price': float(current_price),
                'confidence': float(abs(ensemble_pred) * 100),  
                'direction': 'UP' if ensemble_pred > 0.01 else 'DOWN' if ensemble_pred < -0.01 else 'NEUTRAL',
            }
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None


class TrendAnalyzer:
    """Analyze and identify trading trends and patterns"""
    
    @staticmethod
    def analyze_trend(data: pd.DataFrame) -> Dict:
        """Analyze current trend"""
        try:
            if len(data) < 50:
                return {'trend': 'INSUFFICIENT_DATA'}
            
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            sma_200 = data['Close'].rolling(min(200, len(data))).mean().iloc[-1] if len(data) >= 200 else data['Close'].mean()
            
            current_price = data['Close'].iloc[-1]
            
            if current_price > sma_20 > sma_50 > sma_200:
                trend = 'STRONG_UPTREND'
                probability = 85.0
            elif current_price > sma_20 > sma_50:
                trend = 'UPTREND'
                probability = 75.0
            elif current_price < sma_20 < sma_50 < sma_200:
                trend = 'STRONG_DOWNTREND'
                probability = 85.0
            elif current_price < sma_20 < sma_50:
                trend = 'DOWNTREND'
                probability = 75.0
            else:
                trend = 'SIDEWAYS'
                probability = 50.0
            
            support = data['Low'].rolling(20).min().iloc[-1]
            resistance = data['High'].rolling(20).max().iloc[-1]
            
            return {
                'trend': trend,
                'trend_probability': probability,
                'current_price': float(current_price),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'sma_200': float(sma_200),
                'support': float(support),
                'resistance': float(resistance),
                'distance_to_support': float(((current_price - support) / support * 100) if support > 0 else 0),
                'distance_to_resistance': float(((resistance - current_price) / current_price * 100) if current_price > 0 else 0),
            }
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def identify_patterns(data: pd.DataFrame) -> Dict:
        """Identify candlestick and chart patterns"""
        try:
            if len(data) < 5:
                return {'patterns': []}
            
            patterns = []
            
            if (data['Low'].iloc[-3] > data['Low'].iloc[-2] and 
                data['Low'].iloc[-2] < data['Low'].iloc[-1] and
                abs(data['Low'].iloc[-3] - data['Low'].iloc[-1]) / data['Low'].iloc[-3] < 0.05):
                patterns.append({
                    'name': 'Double Bottom',
                    'type': 'BULLISH',
                    'confidence': 75.0,
                    'location': 'Last 3 candles'
                })
            
            if (data['High'].iloc[-3] < data['High'].iloc[-2] and 
                data['High'].iloc[-2] > data['High'].iloc[-1] and
                abs(data['High'].iloc[-3] - data['High'].iloc[-1]) / data['High'].iloc[-3] < 0.05):
                patterns.append({
                    'name': 'Double Top',
                    'type': 'BEARISH',
                    'confidence': 75.0,
                    'location': 'Last 3 candles'
                })
            
            if len(data) >= 1:
                current = data.iloc[-1]
                body = abs(current['Close'] - current['Open'])
                lower_wick = min(current['Close'], current['Open']) - current['Low']
                
                if lower_wick > body * 2 and body > 0:
                    patterns.append({
                        'name': 'Hammer',
                        'type': 'BULLISH',
                        'confidence': 70.0,
                        'location': 'Last candle'
                    })
            
            return {
                'pattern_count': len(patterns),
                'patterns': patterns,
            }
        except Exception as e:
            logger.error(f"Error identifying patterns: {e}")
            return {'patterns': []}


class SignalGenerator:
    """Generate trading signals based on multiple indicators"""
    
    @staticmethod
    def generate_signal(symbol: str, data: pd.DataFrame) -> Dict:
        """Generate BUY/SELL/HOLD signal"""
        try:
            if data is None or len(data) < 50:
                return {'signal': 'HOLD', 'reason': 'Insufficient data'}
            
            current_price = data['Close'].iloc[-1]
            score = 0  
            reasons = []
            
            trend_data = TrendAnalyzer.analyze_trend(data)
            if 'trend' in trend_data:
                if 'UPTREND' in trend_data['trend']:
                    score += 30
                    reasons.append(f"Uptrend detected ({trend_data['trend']})")
                elif 'DOWNTREND' in trend_data['trend']:
                    score -= 30
                    reasons.append(f"Downtrend detected ({trend_data['trend']})")
            
            delta = data['Close'].diff()
            gain = np.mean(np.maximum(delta, 0))
            loss = np.mean(np.maximum(-delta, 0))
            rsi = 100 - (100 / (1 + (gain / (loss + 1e-10))))
            
            if rsi < 30:
                score += 25
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                score -= 25
                reasons.append(f"RSI overbought ({rsi:.1f})")
            
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            
            if sma_20 > sma_50:
                score += 20
                reasons.append("SMA20 > SMA50 (bullish)")
            else:
                score -= 20
                reasons.append("SMA20 < SMA50 (bearish)")
            
            support = data['Low'].rolling(20).min().iloc[-1]
            resistance = data['High'].rolling(20).max().iloc[-1]
            price_position = (current_price - support) / (resistance - support + 1e-10)
            
            if price_position < 0.3:
                score += 20
                reasons.append("Price near support level")
            elif price_position > 0.7:
                score -= 20
                reasons.append("Price near resistance level")
            
            recent_volume = data['Volume'].iloc[-5:].mean()
            avg_volume = data['Volume'].mean()
            
            if recent_volume > avg_volume * 1.2:
                if score > 0:
                    score += 10
                    reasons.append("Volume surge confirms bullish signal")
                else:
                    score -= 10
                    reasons.append("Volume surge confirms bearish signal")
            
            if score >= 50:
                signal = 'STRONG_BUY'
                confidence = min(95, 50 + score / 2)
            elif score >= 20:
                signal = 'BUY'
                confidence = 50 + score / 2
            elif score <= -50:
                signal = 'STRONG_SELL'
                confidence = min(95, 50 + abs(score) / 2)
            elif score <= -20:
                signal = 'SELL'
                confidence = 50 + abs(score) / 2
            else:
                signal = 'HOLD'
                confidence = 50.0
            
            return {
                'symbol': symbol,
                'signal': signal,
                'score': float(score),
                'confidence': float(confidence),
                'current_price': float(current_price),
                'support': float(support),
                'resistance': float(resistance),
                'rsi': float(rsi),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'reasons': reasons,
            }
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return {'signal': 'HOLD', 'error': str(e)}
