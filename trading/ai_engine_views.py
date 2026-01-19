from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import json

from .ai_formula_engine import (
    TrendFormulas, MomentumFormulas, VolatilityFormulas,
    VolumeFormulas, FundamentalFormulas, AIMetrics, RiskFormulas, FormulaMeta
)
from .market_condition_detector import MarketConditionDetector, MarketCondition
from .trader_type_mapper import TraderTypeMapper, TraderType
from .ai_signal_generator import SignalGenerator


class FormulaCalculatorView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
    
        
        try:
            formula = request.data.get("formula", "").upper()
            prices = request.data.get("prices", [])
            volumes = request.data.get("volumes", [])
            highs = request.data.get("highs", [])
            lows = request.data.get("lows", [])
            parameters = request.data.get("parameters", {})
            
            if not prices:
                return Response(
                    {"error": "Prices list is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = {}
            
            if formula == "SMA":
                period = parameters.get("period", 20)
                result["value"] = TrendFormulas.calculate_sma(prices, period)
                result["formula_name"] = "Simple Moving Average"
            
            elif formula == "EMA":
                period = parameters.get("period", 12)
                result["value"] = TrendFormulas.calculate_ema(prices, period)
                result["formula_name"] = "Exponential Moving Average"
            
            elif formula == "VWAP":
                if not volumes:
                    return Response({"error": "Volumes required for VWAP"}, status=status.HTTP_400_BAD_REQUEST)
                result["value"] = TrendFormulas.calculate_vwap(prices, volumes)
                result["formula_name"] = "Volume Weighted Average Price"
            
            elif formula == "RSI":
                period = parameters.get("period", 14)
                result["value"] = MomentumFormulas.calculate_rsi(prices, period)
                result["interpretation"] = self._interpret_rsi(result["value"])
                result["formula_name"] = "Relative Strength Index"
            
            elif formula == "MACD":
                macd, signal, histogram = MomentumFormulas.calculate_macd(prices)
                result["macd"] = macd
                result["signal"] = signal
                result["histogram"] = histogram
                result["formula_name"] = "MACD"
            
            elif formula == "ROC":
                period = parameters.get("period", 12)
                result["value"] = MomentumFormulas.calculate_roc(prices, period)
                result["formula_name"] = "Rate of Change"
            
            elif formula == "BOLLINGER_BANDS":
                if not highs or not lows:
                    return Response({"error": "Highs and lows required"}, status=status.HTTP_400_BAD_REQUEST)
                period = parameters.get("period", 20)
                std_dev = parameters.get("std_dev", 2.0)
                upper, middle, lower = VolatilityFormulas.calculate_bollinger_bands(prices, period, std_dev)
                result["upper"] = upper
                result["middle"] = middle
                result["lower"] = lower
                result["width"] = upper - lower
                result["formula_name"] = "Bollinger Bands"
            
            elif formula == "ATR":
                if not highs or not lows:
                    return Response({"error": "Highs and lows required"}, status=status.HTTP_400_BAD_REQUEST)
                period = parameters.get("period", 14)
                result["value"] = VolatilityFormulas.calculate_atr(highs, lows, prices, period)
                result["formula_name"] = "Average True Range"
            
            elif formula == "OBV":
                if not volumes:
                    return Response({"error": "Volumes required for OBV"}, status=status.HTTP_400_BAD_REQUEST)
                result["value"] = VolumeFormulas.calculate_obv(prices, volumes)
                result["formula_name"] = "On-Balance Volume"
            
            elif formula == "VOLUME_OSCILLATOR":
                if not volumes:
                    return Response({"error": "Volumes required"}, status=status.HTTP_400_BAD_REQUEST)
                short_period = parameters.get("short_period", 12)
                long_period = parameters.get("long_period", 26)
                result["value"] = VolumeFormulas.calculate_volume_oscillator(volumes, short_period, long_period)
                result["formula_name"] = "Volume Oscillator"
            
            elif formula == "SHARPE_RATIO":
                risk_free_rate = parameters.get("risk_free_rate", 0.05)
                periods = parameters.get("periods_per_year", 252)
                result["value"] = AIMetrics.calculate_sharpe_ratio(prices, risk_free_rate, periods)
                result["formula_name"] = "Sharpe Ratio"
            
            elif formula == "SORTINO_RATIO":
                target_return = parameters.get("target_return", 0.0)
                periods = parameters.get("periods_per_year", 252)
                result["value"] = AIMetrics.calculate_sortino_ratio(prices, target_return, periods)
                result["formula_name"] = "Sortino Ratio"
            
            elif formula == "MAX_DRAWDOWN":
                result["value"] = AIMetrics.calculate_max_drawdown(prices)
                result["formula_name"] = "Maximum Drawdown"
            
            else:
                return Response(
                    {"error": f"Unknown formula: {formula}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if rsi > 70:
            return "OVERBOUGHT - Potential reversal or pullback"
        elif rsi < 30:
            return "OVERSOLD - Potential bounce or recovery"
        elif rsi > 60:
            return "Bullish momentum"
        elif rsi < 40:
            return "Bearish momentum"
        else:
            return "Neutral"


class MarketAnalysisView(APIView):
    """Analyze market conditions"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Analyze market condition
        
        Expects:
        {
            "prices": [100, 101, 102, ...],
            "volumes": [1000, 1100, ...],
            "highs": [102, 103, ...],
            "lows": [99, 100, ...]
        }
        """
        
        try:
            prices = request.data.get("prices", [])
            volumes = request.data.get("volumes", [])
            highs = request.data.get("highs", [])
            lows = request.data.get("lows", [])
            
            if not prices or len(prices) < 50:
                return Response(
                    {"error": "At least 50 price points required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            detector = MarketConditionDetector()
            analysis = detector.analyze_market(prices, volumes, highs, lows)
            
            return Response({
                "market_condition": analysis.condition.value,
                "trend": analysis.trend,
                "trend_strength": analysis.trend_strength.name,
                "volatility_regime": analysis.volatility_regime.value,
                "scores": {
                    "trend_score": round(analysis.trend_score, 2),
                    "momentum_score": round(analysis.momentum_score, 2),
                    "volatility_score": round(analysis.volatility_score, 2),
                    "volume_strength": round(analysis.volume_strength, 2),
                    "confidence": round(analysis.confidence_level, 2),
                },
                "indicators": {
                    "sma20": round(analysis.sma20, 2),
                    "sma50": round(analysis.sma50, 2),
                    "ema12": round(analysis.ema12, 2),
                    "ema26": round(analysis.ema26, 2),
                    "rsi": round(analysis.rsi, 2),
                    "atr": round(analysis.atr, 2),
                },
                "recommended_indicators": analysis.recommended_indicators,
                "explanation": analysis.explanation,
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TraderTypeMapperView(APIView):
    """Get trader type recommendations"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all trader type profiles"""
        try:
            trader_type = request.query_params.get("type")
            
            if trader_type:
                try:
                    trader_enum = TraderType[trader_type.upper()]
                except KeyError:
                    return Response(
                        {"error": f"Unknown trader type: {trader_type}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                profile = TraderTypeMapper.get_profile(trader_enum)
                guidelines = TraderTypeMapper.get_position_size_guidelines(trader_enum)
                
                return Response({
                    "trader_type": profile.trader_type.value,
                    "description": profile.description,
                    "time_horizon": profile.time_horizon,
                    "risk_tolerance": profile.risk_tolerance,
                    "primary_formulas": profile.primary_formulas,
                    "secondary_formulas": profile.secondary_formulas,
                    "avoid_formulas": profile.avoid_formulas,
                    "holding_period": profile.holding_period,
                    "max_risk_per_trade": profile.max_risk_per_trade,
                    "ideal_market_conditions": profile.ideal_market_conditions,
                    "position_sizing_guidelines": guidelines,
                }, status=status.HTTP_200_OK)
            
            else:
                all_profiles = {}
                for trader_type_enum in TraderType:
                    profile = TraderTypeMapper.get_profile(trader_type_enum)
                    all_profiles[trader_type_enum.value] = {
                        "description": profile.description,
                        "time_horizon": profile.time_horizon,
                        "primary_formulas": profile.primary_formulas,
                    }
                
                return Response(all_profiles, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AISignalGeneratorView(APIView):
    """Generate AI-powered trading signals"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Generate trading signal
        
        Expects:
        {
            "symbol": "AAPL",
            "current_price": 150.50,
            "prices": [140, 141, 142, ...],
            "volumes": [1000000, 1100000, ...],
            "highs": [142, 143, ...],
            "lows": [139, 140, ...],
            "trader_type": "SWING",
            "capital": 100000,
            "max_risk_percent": 1.0
        }
        """
        
        try:
            symbol = request.data.get("symbol", "UNKNOWN")
            current_price = request.data.get("current_price", 0)
            prices = request.data.get("prices", [])
            volumes = request.data.get("volumes", [])
            highs = request.data.get("highs", [])
            lows = request.data.get("lows", [])
            trader_type_str = request.data.get("trader_type", "SWING").upper()
            capital = request.data.get("capital", 100000)
            max_risk_percent = request.data.get("max_risk_percent", 1.0)
            
            if not prices or len(prices) < 50:
                return Response(
                    {"error": "At least 50 price points required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                trader_type = TraderType[trader_type_str]
            except KeyError:
                return Response(
                    {"error": f"Unknown trader type: {trader_type_str}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            generator = SignalGenerator()
            signal = generator.generate_signal(
                symbol=symbol,
                current_price=current_price,
                prices=prices,
                volumes=volumes,
                highs=highs,
                lows=lows,
                trader_type=trader_type,
                capital=capital,
                max_risk_percent=max_risk_percent
            )
            
            return Response({
                "signal": signal.signal.value,
                "confidence": round(signal.confidence, 2),
                "entry_price": round(signal.entry_price, 2),
                "stop_loss": round(signal.stop_loss, 2),
                "target_1": round(signal.target_1, 2),
                "target_2": round(signal.target_2, 2) if signal.target_2 else None,
                "target_3": round(signal.target_3, 2) if signal.target_3 else None,
                "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
                "position_size": signal.position_size,
                "max_risk_amount": round(signal.max_risk_amount, 2),
                "formulas_used": signal.formulas_used,
                "formula_explanations": signal.formula_explanations,
                "trader_type": signal.trader_type,
                "trader_suitability": signal.trader_suitability,
                "market_condition": signal.market_condition,
                "confidence_reason": signal.confidence_reason,
                "generated_at": signal.generated_at,
                "valid_until": signal.valid_until,
                "technical_indicators": signal.technical_indicators,
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FormularMetadataView(APIView):
    """Get formula metadata and descriptions"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get formula information"""
        try:
            formula = request.query_params.get("formula")
            
            if formula:
                formula_upper = formula.upper()
                if formula_upper in FormulaMeta.FORMULA_INFO:
                    info = FormulaMeta.FORMULA_INFO[formula_upper]
                    return Response(info, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": f"Unknown formula: {formula}"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            else:
                return Response(FormulaMeta.FORMULA_INFO, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
