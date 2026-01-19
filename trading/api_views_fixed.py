
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import datetime
import logging

from .models import (
    Stock, StockAnalysis, TradeRecommendation, TradeOrder,
    Portfolio, RiskAssessment, AlternativeInvestment,
    PaperTrade, SmartAlert
)
from .serializers import (
    StockSerializer, StockAnalysisSerializer, TradeRecommendationSerializer,
)
from .error_handler import (
    ValidationError, NotFoundError, AuthenticationError,
    DataUnavailableError, AnalysisError, PayloadValidator,
    ResponseFormatter, SafeAnalysisExecutor, APIError
)
from .market_data_service import MarketDataService, MarketCalendar
from .services import (
    TechnicalAnalysisService, RiskManagementService,
    TradeRecommendationService, SignalGenerationService,
    RiskAnalyzerService
)

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return ResponseFormatter.success({
            'status': 'healthy',
            'version': '2.0',
            'market_status': MarketDataService.get_market_status(),
        }, status_code=status.HTTP_200_OK)


class ImprovedStockAnalysisViewSet(viewsets.ModelViewSet):
    """Improved Stock Analysis with error handling and validation"""
    
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [AllowAny]
    lookup_field = 'symbol'
    
    def retrieve(self, request, symbol=None):
        """Get stock by symbol with improved error handling"""
        try:
            valid, error = PayloadValidator.validate_stock_symbol(symbol)
            if not valid:
                error.log()
                return error.to_response()
            
            stock = self.get_object()
            serializer = self.get_serializer(stock)
            return ResponseFormatter.success(serializer.data, f"Stock {symbol} found")
            
        except Exception as e:
            error = NotFoundError("Stock", symbol)
            error.log()
            return error.to_response()
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, symbol=None):
        """Analyze stock with complete error handling"""
        try:
            valid, err = PayloadValidator.validate_stock_symbol(symbol)
            if not valid:
                err.log()
                return err.to_response()
            
            stock = self.get_object()
            
            market_data = MarketDataService.get_market_data(symbol)
            
            is_valid, validation_msg = MarketDataService.validate_data_for_analysis(market_data)
            if not is_valid:
                error = DataUnavailableError(validation_msg)
                error.log()
                return error.to_response()
            
            success, analysis_result, exec_error = SafeAnalysisExecutor.execute_analysis(
                TechnicalAnalysisService.analyze_technical,
                symbol=symbol,
                prices=[d['close'] for d in market_data['data']],
                volumes=[d['volume'] for d in market_data['data']],
                highs=[d['high'] for d in market_data['data']],
                lows=[d['low'] for d in market_data['data']]
            )
            
            if not success:
                return exec_error.to_response()
            
            market_status = MarketDataService.get_market_status()
            
            result = {
                'symbol': symbol,
                'analysis': analysis_result,
                'market_data_source': market_data.get('source', 'UNKNOWN'),
                'market_status': market_status['status'],
                'data_type': 'LIVE' if market_status['is_open'] else 'DELAYED/HISTORICAL',
                'timestamp': datetime.now().isoformat(),
            }
            
            return ResponseFormatter.success(result, f"Analysis complete for {symbol}")
            
        except Exception as e:
            logger.exception(f"Unexpected error analyzing {symbol}")
            error = AnalysisError(str(e))
            error.log()
            return error.to_response()


class ImprovedTradeRecommendationViewSet(viewsets.ModelViewSet):
    """Improved Trade Recommendation with validation and safety checks"""
    
    queryset = TradeRecommendation.objects.all()
    serializer_class = TradeRecommendationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle POST to generate recommendation"""
        return self.generate(request)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate trade recommendation with comprehensive validation"""
        try:
            required_fields = ['stock_symbol', 'trading_style', 'capital']
            valid, error = PayloadValidator.validate_required_fields(request.data, required_fields)
            if not valid:
                error.log()
                return error.to_response()
            
            stock_symbol = request.data.get('stock_symbol', '').strip().upper()
            trading_style = request.data.get('trading_style', 'SWING').upper()
            capital = request.data.get('capital')
            
            valid, error = PayloadValidator.validate_stock_symbol(stock_symbol)
            if not valid:
                error.log()
                return error.to_response()
            
            valid, error = PayloadValidator.validate_trading_style(trading_style)
            if not valid:
                error.log()
                return error.to_response()
            
            valid, error = PayloadValidator.validate_numeric(capital, 'capital', min_val=1000, max_val=10000000)
            if not valid:
                error.log()
                return error.to_response()
            
            capital = Decimal(str(capital))
            
            try:
                stock = Stock.objects.get(symbol=stock_symbol)
            except Stock.DoesNotExist:
                stock = Stock.objects.create(
                    symbol=stock_symbol,
                    name=stock_symbol,
                    sector='Unknown'
                )
                logger.info(f"Created new stock record: {stock_symbol}")
            
            market_data = MarketDataService.get_market_data(stock_symbol)
            
            is_valid, validation_msg = MarketDataService.validate_data_for_analysis(market_data)
            if not is_valid:
                error = DataUnavailableError(validation_msg)
                error.log()
                return error.to_response()
            
            prices = [d['close'] for d in market_data['data']]
            volumes = [d['volume'] for d in market_data['data']]
            highs = [d['high'] for d in market_data['data']]
            lows = [d['low'] for d in market_data['data']]
            
            success, rec_data, exec_error = SafeAnalysisExecutor.execute_analysis(
                TradeRecommendationService.generate_recommendation,
                symbol=stock_symbol,
                prices=prices,
                volumes=volumes,
                highs=highs,
                lows=lows,
                trading_style=trading_style,
                capital=float(capital)
            )
            
            if not success:
                return exec_error.to_response()
            
            market_status = MarketDataService.get_market_status()
            
            try:
                recommendation = TradeRecommendation.objects.create(
                    stock=stock,
                    trading_style=trading_style,
                    signal=rec_data.get('signal', 'HOLD'),
                    entry_price=Decimal(str(rec_data.get('entry_price', 0))),
                    stop_loss=Decimal(str(rec_data.get('stop_loss', 0))),
                    target_1=Decimal(str(rec_data.get('targets', [0])[0])),
                    risk_reward_ratio=Decimal(str(rec_data.get('risk_reward_ratio', 0))),
                    confidence_level=rec_data.get('confidence', 50),
                )
            except Exception as e:
                logger.warning(f"Could not save recommendation to DB: {e}")
                recommendation = None
            
            result = {
                'recommendation_id': recommendation.id if recommendation else None,
                'symbol': stock_symbol,
                'signal': rec_data.get('signal'),
                'entry_price': float(rec_data.get('entry_price', 0)),
                'stop_loss': float(rec_data.get('stop_loss', 0)),
                'targets': rec_data.get('targets', []),
                'confidence': rec_data.get('confidence', 50),
                'risk_reward_ratio': float(rec_data.get('risk_reward_ratio', 0)),
                'position_size': rec_data.get('position_size'),
                'market_status': market_status['status'],
                'data_type': 'LIVE' if market_status['is_open'] else 'DELAYED',
                'formulas_used': rec_data.get('formulas_used', []),
                'explanations': rec_data.get('explanations', {}),
                'generated_at': datetime.now().isoformat(),
            }
            
            return ResponseFormatter.success(
                result,
                f"Recommendation generated for {stock_symbol}",
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.exception("Error generating recommendation")
            error = AnalysisError(f"Error generating recommendation: {str(e)}")
            error.log()
            return error.to_response()


class ImprovedIntradaySignalViewSet(viewsets.ModelViewSet):
    """Improved Intraday Signal generation"""
    
    queryset = PaperTrade.objects.none()
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Generate intraday signal"""
        try:
            required_fields = ['stock_symbol', 'timeframe']
            valid, error = PayloadValidator.validate_required_fields(request.data, required_fields)
            if not valid:
                error.log()
                return error.to_response()
            
            stock_symbol = request.data.get('stock_symbol', '').strip().upper()
            timeframe = request.data.get('timeframe', '5m')
            
            valid, error = PayloadValidator.validate_stock_symbol(stock_symbol)
            if not valid:
                error.log()
                return error.to_response()
            
            market_status = MarketDataService.get_market_status()
            
            market_data = MarketDataService.get_market_data(stock_symbol)
            
            is_valid, validation_msg = MarketDataService.validate_data_for_analysis(market_data)
            if not is_valid:
                error = DataUnavailableError(validation_msg)
                return error.to_response()
            
            prices = [d['close'] for d in market_data['data']]
            volumes = [d['volume'] for d in market_data['data']]
            highs = [d['high'] for d in market_data['data']]
            lows = [d['low'] for d in market_data['data']]
            
            success, signal_data, exec_error = SafeAnalysisExecutor.execute_analysis(
                SignalGenerationService.generate_intraday_signal,
                symbol=stock_symbol,
                prices=prices,
                volumes=volumes,
                highs=highs,
                lows=lows,
                timeframe=timeframe
            )
            
            if not success:
                return exec_error.to_response()
            
            result = {
                'symbol': stock_symbol,
                'timeframe': timeframe,
                'signal': signal_data.get('signal'),
                'confidence': signal_data.get('confidence', 50),
                'entry_price': signal_data.get('entry_price'),
                'stop_loss': signal_data.get('stop_loss'),
                'targets': signal_data.get('targets', []),
                'market_status': market_status['status'],
                'data_type': 'LIVE' if market_status['is_open'] else 'DELAYED',
                'generated_at': datetime.now().isoformat(),
            }
            
            return ResponseFormatter.success(result, "Intraday signal generated")
            
        except Exception as e:
            logger.exception("Error generating intraday signal")
            error = AnalysisError(str(e))
            error.log()
            return error.to_response()
