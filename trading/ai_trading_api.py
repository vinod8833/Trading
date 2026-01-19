from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import logging
import json
from datetime import datetime

from .ai_trading_system import (
    AITradingSystem,
    DataIntakeEngine,
    MarketStateDetector,
    SignalGenerationEngine,
    UserFacingOutput,
    DataQualityLevel
)
from .models import Stock, StockAnalysis
from .market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class ComprehensiveTradeAnalysisView(APIView):
    """
    Complete AI-driven trading analysis endpoint
    Input: Stock symbol + market data
    Output: Clean, reliable trading guidance with full transparency
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Generate trading signal with complete data validation
        
        Request:
        {
            "symbol": "INFY",
            "capital": 100000,
            "trader_type": "SWING",
            "prices": [100, 101, 102, ...],  (50+ required)
            "volumes": [1000000, ...],
            "highs": [101, 102, 103, ...],
            "lows": [99, 100, 101, ...],
            "current_price": 102.5,
            "indicators": { "atr": 1.5, "rsi": 65, ... }
        }
        
        Response:
        {
            "status": "READY" | "WAITING" | "NO_TRADE" | "ERROR",
            "message": "Human-readable trading guidance",
            "signal": "BUY" | "SELL" | "HOLD",
            "confidence": 0-100,
            "entry_price": 102.50,
            "target": "Target: ₹105.00 (+2.4%)",
            "stop": "Stop Loss: ₹100.50",
            "risk_reward": "Risk/Reward: 1:2.3",
            "market_status": "LIVE" | "HISTORICAL",
            "execution_timing": "IMMEDIATE" | "ON_NEXT_OPEN",
            "confidence_reasons": ["Reason 1", "Reason 2"],
            "warnings": ["Warning 1"] or null,
            "technical": { ... full technical details ... }
        }
        """
        try:
            symbol = request.data.get('symbol', '').strip().upper()
            capital = float(request.data.get('capital', 100000))
            trader_type = request.data.get('trader_type', 'SWING').upper()
            
            if not symbol:
                return Response(
                    {'error': 'Symbol required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if capital < 1000 or capital > 10000000:
                return Response(
                    {'error': f'Capital must be between ₹1,000 and ₹10,000,000, got ₹{capital}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            market_data = {
                'current_price': float(request.data.get('current_price', 0)),
                'prices': request.data.get('prices', []),
                'volumes': request.data.get('volumes', []),
                'highs': request.data.get('highs', []),
                'lows': request.data.get('lows', []),
                'indicators': request.data.get('indicators', {}),
                'age_minutes': int(request.data.get('age_minutes', 0))
            }
            
            result = AITradingSystem.process_trade_request(
                symbol=symbol,
                capital=capital,
                trader_type=trader_type,
                market_data=market_data
            )
            
            if result['status'] == 'ERROR':
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error in trade analysis: {e}")
            return Response(
                {'error': 'Internal server error', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DataQualityReportView(APIView):
    """
    Detailed data quality assessment
    Helps users understand data reliability for their analysis
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Assess data quality of provided OHLC data
        
        Request:
        {
            "symbol": "INFY",
            "prices": [...],
            "volumes": [...],
            "highs": [...],
            "lows": [...],
            "age_minutes": 5
        }
        
        Response:
        {
            "symbol": "INFY",
            "data_quality_level": "pristine" | "clean" | "acceptable" | "degraded" | "unusable",
            "completeness": 99.5,
            "freshness_minutes": 5,
            "is_safe_for_trading": true,
            "confidence_penalty": 0,
            "candles_processed": 100,
            "candles_removed": 0,
            "issues": [],
            "warnings": ["Warning 1"],
            "recommendation": "Proceed with trading"
        }
        """
        try:
            symbol = request.data.get('symbol', 'UNKNOWN')
            
            is_valid, errors, prices, volumes, highs, lows = \
                DataIntakeEngine.validate_ohlc_series(
                    request.data.get('prices', []),
                    request.data.get('volumes', []),
                    request.data.get('highs', []),
                    request.data.get('lows', [])
                )
            
            if not is_valid:
                return Response({
                    'symbol': symbol,
                    'data_quality_level': 'unusable',
                    'is_safe_for_trading': False,
                    'issues': errors,
                    'recommendation': 'Cannot use this data - issues detected'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            import pandas as pd
            df = pd.DataFrame({
                'close': prices,
                'volume': volumes,
                'high': highs,
                'low': lows
            })
            
            market_status = MarketStateDetector.get_market_status()
            age_minutes = int(request.data.get('age_minutes', 0))
            
            quality_report = DataIntakeEngine.assess_data_quality(
                df, symbol, market_status.is_trading_allowed,
                datetime.now() - pd.Timedelta(minutes=age_minutes)
            )
            
            return Response({
                'symbol': symbol,
                'data_quality_level': quality_report.level.value,
                'completeness': quality_report.completeness,
                'freshness_minutes': quality_report.freshness_minutes,
                'is_safe_for_trading': quality_report.is_safe_for_trading,
                'confidence_penalty': quality_report.confidence_penalty,
                'candles_processed': len(prices),
                'issues': quality_report.issues,
                'warnings': quality_report.warnings,
                'recommendation': (
                    '✓ Data is excellent, proceed with confidence' if quality_report.can_proceed()
                    else '⚠ Data has issues, use with caution'
                    if quality_report.is_safe_for_trading
                    else 'Data not suitable for trading'
                )
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error assessing data quality: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MarketStatusView(APIView):
    """
    Current market status and data freshness information
    Helps users understand data source and signal reliability
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get current market status
        
        Response:
        {
            "market_state": "open" | "closed" | "holiday" | "low_liquidity",
            "is_trading_allowed": true/false,
            "data_type": "LIVE" | "HISTORICAL" | "DELAYED",
            "message": "Market is OPEN - Using LIVE data",
            "recommendation": "Execute signals immediately with market orders",
            "next_open_time": "2026-01-20T09:15:00",
            "confidence_applicable": true/false,
            "timestamp": "2026-01-19T14:30:00"
        }
        """
        market_status = MarketStateDetector.get_market_status()
        
        return Response({
            'market_state': market_status.state.value,
            'is_trading_allowed': market_status.is_trading_allowed,
            'data_type': market_status.data_type,
            'message': market_status.message,
            'recommendation': market_status.get_recommendation(),
            'next_open_time': market_status.next_open_time.isoformat() if market_status.next_open_time else None,
            'confidence_applicable': market_status.confidence_applicable,
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)


class SignalExplanationView(APIView):
    """
    Detailed explanation of why a signal was generated or rejected
    Builds user trust through transparency
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Get detailed explanation for a trading signal
        
        Request:
        {
            "symbol": "INFY",
            "prices": [...],
            "volumes": [...],
            "highs": [...],
            "lows": [...],
            "current_price": 102.5,
            "capital": 100000
        }
        
        Response:
        {
            "symbol": "INFY",
            "explanation": "Full human-readable explanation",
            "signal_generated": true/false,
            "signal_type": "BUY" | "SELL" | "HOLD" | "NO_SIGNAL",
            "confidence": 0-100,
            "data_quality": "pristine" | "clean" | ...,
            "market_status": "open" | "closed" | ...,
            "key_factors": [
                "Trend: Bullish (50-day EMA > 200-day EMA)",
                "Momentum: Positive (RSI 65, MACD bullish crossover)",
                "Volume: Adequate (125% of 20-day average)",
                "Risk/Reward: Acceptable (1:2.3)"
            ],
            "concerns": [
                "Data is 30 minutes old"
            ],
            "recommendation": "Execute BUY at market with stop at 100.50"
        }
        """
        try:
            symbol = request.data.get('symbol', 'UNKNOWN')
            
            market_data = {
                'current_price': float(request.data.get('current_price', 0)),
                'prices': request.data.get('prices', []),
                'volumes': request.data.get('volumes', []),
                'highs': request.data.get('highs', []),
                'lows': request.data.get('lows', []),
                'indicators': request.data.get('indicators', {}),
                'age_minutes': int(request.data.get('age_minutes', 0))
            }
            
            capital = float(request.data.get('capital', 100000))
            
            signal = SignalGenerationEngine.generate_signal(
                symbol=symbol,
                prices=market_data['prices'],
                volumes=market_data['volumes'],
                highs=market_data['highs'],
                lows=market_data['lows'],
                current_price=market_data['current_price'],
                capital=capital
            )
            
            if not signal.is_valid:
                explanation = f"Cannot generate trading signal: {signal.errors[0]}"
                signal_generated = False
            else:
                explanation = f"✓ {signal.signal_type} Signal Generated"
                signal_generated = True
            
            return Response({
                'symbol': symbol,
                'explanation': explanation,
                'signal_generated': signal_generated,
                'signal_type': signal.signal_type,
                'confidence': round(signal.confidence, 1),
                'data_quality': signal.data_quality.value,
                'market_status': signal.market_status.value,
                'key_factors': signal.confidence_reasons,
                'concerns': signal.warnings + signal.errors,
                'recommendation': (
                    f"Execute {signal.signal_type.lower()} at ₹{signal.entry_price:.2f} "
                    f"with stop at ₹{signal.stop_loss:.2f} and target at ₹{signal.target_1:.2f}"
                    if signal_generated
                    else 'Wait for clearer market conditions'
                )
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error generating explanation: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignalValidationView(APIView):
    """
    Validate if a proposed trade setup follows senior trader rules
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Validate a trade setup against trader rules
        
        Request:
        {
            "symbol": "INFY",
            "signal_type": "BUY",
            "entry_price": 102.50,
            "target_price": 105.00,
            "stop_loss": 100.50,
            "current_price": 102.50,
            "capital": 100000
        }
        
        Response:
        {
            "is_valid": true/false,
            "violations": [],
            "warnings": ["Risk/Reward could be higher"],
            "risk_reward_ratio": 2.3,
            "risk_score": 25,
            "recommendation": "Setup is valid, proceed with caution"
        }
        """
        from .ai_trading_system import SeniorTraderRulesEngine
        
        try:
            assessment = SeniorTraderRulesEngine.validate_signal_setup(
                entry_price=float(request.data.get('entry_price', 0)),
                stop_loss=float(request.data.get('stop_loss', 0)),
                target_1=float(request.data.get('target_price', 0)),
                target_2=float(request.data.get('target_price_2', 0)) if request.data.get('target_price_2') else None,
                current_price=float(request.data.get('current_price', 0)),
                capital=float(request.data.get('capital', 100000)),
                signal_type=request.data.get('signal_type', 'BUY')
            )
            
            return Response({
                'is_valid': assessment.passes_rules,
                'violations': assessment.violations,
                'warnings': assessment.warnings,
                'risk_score': round(assessment.risk_score, 1),
                'recommendation': (
                    '✓ Setup is valid' if assessment.passes_rules
                    else 'Setup has violations'
                )
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception(f"Error validating signal: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
