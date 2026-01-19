
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
import logging
import json

from trading.signal_generation import get_signal_monitor
from trading.data_integration import get_data_engine, is_market_open
from trading.technical_indicators import TechnicalIndicatorsEngine
from trading.prediction_engine import PredictionEngine

logger = logging.getLogger(__name__)


class GenerateTradingSignalView(APIView):
    """
    Generate comprehensive trading signal
    
    Endpoint: POST /api/ai/generate-signal/
    
    Request:
    {
        "symbol": "INFY",
        "capital": 100000,
        "trader_type": "SWING"  # INTRADAY, SWING, POSITIONAL
    }
    
    Response:
    {
        "status": "SUCCESS",
        "signal": {
            "type": "BUY",
            "confidence": 78.5,
            "entry": 1680.50,
            "stop_loss": 1670.20,
            "target_1": 1695.80,
            "target_2": 1715.30,
            "target_3": 1735.80
        },
        "market": {
            "status": "LIVE",
            "message": "Market is OPEN"
        },
        "analysis": { ... },
        "timestamp": "2026-01-19T14:30:00"
    }
    """
    
    def post(self, request):
        try:
            symbol = request.data.get("symbol", "").upper()
            capital = float(request.data.get("capital", 100000))
            trader_type = request.data.get("trader_type", "SWING")
            
            # Validate
            if not symbol:
                return Response(
                    {"error": "Symbol is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Generating signal for {symbol} (Capital: ₹{capital})")
            
            # Get signal
            signal_monitor = get_signal_monitor()
            signal_monitor.add_signal_watch(symbol, capital)
            signal = signal_monitor.get_updated_signal(symbol)
            
            if not signal:
                return Response(
                    {"error": "Could not generate signal"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            signal["trader_type"] = trader_type
            signal["capital"] = capital
            signal["market_open"] = is_market_open()
            
            return Response(signal, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in signal generation: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FetchMarketDataView(APIView):
    """
    Fetch complete market data for a symbol
    
    Endpoint: GET /api/ai/market-data/
    Query Params: symbol, data_type (QUOTE, HISTORICAL, INTRADAY, ALL)
    
    Response:
    {
        "symbol": "INFY",
        "quote": { ... live quote ... },
        "historical": { ... daily candles ... },
        "intraday": { ... 5-minute candles ... },
        "timestamp": "2026-01-19T14:30:00"
    }
    """
    
    def get(self, request):
        try:
            symbol = request.query_params.get("symbol", "").upper()
            data_type = request.query_params.get("data_type", "ALL")
            
            if not symbol:
                return Response(
                    {"error": "Symbol is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Fetching market data for {symbol} ({data_type})")
            
            data_engine = get_data_engine()
            
            response_data = {"symbol": symbol}
            
            if data_type in ["QUOTE", "ALL"]:
                response_data["quote"] = data_engine.get_live_quote(symbol)
            
            if data_type in ["HISTORICAL", "ALL"]:
                response_data["historical"] = data_engine.get_historical_data(symbol)
            
            if data_type in ["INTRADAY", "ALL"]:
                response_data["intraday"] = data_engine.get_intraday_data(symbol)
            
            response_data["market_open"] = is_market_open()
            response_data["data_sources_available"] = ["NSE", "YFINANCE"]
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalculateIndicatorsView(APIView):
    """
    Calculate technical indicators
    
    Endpoint: POST /api/ai/calculate-indicators/
    
    Request:
    {
        "symbol": "INFY",
        "candles": [
            {"open": 1670, "high": 1680, "low": 1665, "close": 1675, "volume": 1000000},
            ...
        ]
    }
    
    Response:
    {
        "symbol": "INFY",
        "indicators": {
            "trend": { ema_20, ema_50, ema_100, ema_200 },
            "momentum": { rsi, macd_line, macd_signal, ... },
            "volatility": { atr, atr_percent },
            "volume": { vwap, volume_trend },
            "levels": { support_1, resistance_1, pivot }
        }
    }
    """
    
    def post(self, request):
        try:
            symbol = request.data.get("symbol", "").upper()
            candles = request.data.get("candles", [])
            
            if not symbol or not candles:
                return Response(
                    {"error": "Symbol and candles are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(candles) < 50:
                return Response(
                    {"error": f"Need at least 50 candles, got {len(candles)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Calculating indicators for {symbol}")
            
            engine = TechnicalIndicatorsEngine(symbol)
            indicators = engine.calculate_all(candles)
            
            if not indicators:
                return Response(
                    {"error": "Could not calculate indicators"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(indicators.to_dict(), status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PredictPriceMovementView(APIView):
    """
    Predict 5-minute price movement
    
    Endpoint: POST /api/ai/predict-movement/
    
    Request:
    {
        "symbol": "INFY",
        "candles": [ ... intraday 5m candles ... ],
        "indicators": { ... technical indicators ... },
        "current_price": 1680.50
    }
    
    Response:
    {
        "symbol": "INFY",
        "direction": "UP",
        "confidence": 75.5,
        "predicted_price": 1682.75,
        "predicted_change_percent": 0.34,
        "risk_reward": { ... }
    }
    """
    
    def post(self, request):
        try:
            symbol = request.data.get("symbol", "").upper()
            candles = request.data.get("candles", [])
            indicators = request.data.get("indicators", {})
            current_price = float(request.data.get("current_price", 0))
            
            if not all([symbol, candles, current_price]):
                return Response(
                    {"error": "Symbol, candles, and current_price are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Predicting 5-min movement for {symbol}")
            
            indicators_dict = indicators if indicators else {}
            
            engine = PredictionEngine(symbol)
            prediction = engine.predict_5min_movement(candles, indicators_dict, current_price)
            
            if not prediction:
                return Response(
                    {"error": "Could not generate prediction"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(prediction.to_dict(), status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MarketStatusView(APIView):
    """
    Get current market status
    
    Endpoint: GET /api/ai/market-status/
    
    Response:
    {
        "market_open": true,
        "market_hours": "9:15 AM - 3:30 PM IST",
        "message": "Market is OPEN",
        "data_type": "LIVE",
        "recommendation": "Use live signals"
    }
    """
    
    def get(self, request):
        try:
            market_open = is_market_open()
            
            return Response({
                "market_open": market_open,
                "market_hours": "9:15 AM - 3:30 PM IST (Weekdays only)",
                "message": "Market is OPEN" if market_open else "Market is CLOSED",
                "data_type": "LIVE" if market_open else "HISTORICAL",
                "recommendation": "Use live signals for immediate trades" if market_open else "Use for planning next session trades",
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in market status: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshAllSignalsView(APIView):
    """
    Refresh all monitored signals
    
    Endpoint: GET /api/ai/refresh-signals/
    
    Response:
    {
        "count": 5,
        "signals": {
            "INFY": { ... signal ... },
            "TCS": { ... signal ... },
            ...
        },
        "timestamp": "2026-01-19T14:30:00"
    }
    """
    
    def get(self, request):
        try:
            logger.info("Refreshing all monitored signals")
            
            signal_monitor = get_signal_monitor()
            signals = signal_monitor.refresh_all_signals()
            
            return Response({
                "count": len(signals),
                "signals": signals,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error refreshing signals: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DataQualityCheckView(APIView):
    """
    Check data quality for a symbol
    
    Endpoint: GET /api/ai/data-quality/?symbol=INFY
    
    Response:
    {
        "symbol": "INFY",
        "is_valid": true,
        "quality": "GOOD",
        "issues": [],
        "warnings": [],
        "recommendations": "Data is ready for analysis"
    }
    """
    
    def get(self, request):
        try:
            symbol = request.query_params.get("symbol", "").upper()
            
            if not symbol:
                return Response(
                    {"error": "Symbol is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Checking data quality for {symbol}")
            
            data_engine = get_data_engine()
            market_data = data_engine.get_complete_market_data(symbol)
            quality = data_engine.validate_data_quality(symbol, market_data)
            
            return Response(quality, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error checking data quality: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
