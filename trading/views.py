"""
REST API Views for KVK Trading System
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import datetime

from .models import (
    Stock, StockAnalysis, TradeRecommendation, TradeOrder,
    Portfolio, RiskAssessment, AlternativeInvestment,
    PaperTrade, SmartAlert, MarketSummary, PortfolioHealth,
    TradingMistake, AIExplanation, InvestmentPlan
)
from .serializers import (
    StockSerializer, StockAnalysisSerializer, TradeRecommendationSerializer,
    TradeOrderSerializer, PortfolioSerializer, RiskAssessmentSerializer,
    AlternativeInvestmentSerializer, PaperTradeSerializer, SmartAlertSerializer,
    MarketSummarySerializer, PortfolioHealthSerializer, TradingMistakeSerializer,
    AIExplanationSerializer, InvestmentPlanSerializer, SignalResponseSerializer,
    RiskAnalysisResponseSerializer, MarketSummaryResponseSerializer,
    AIExplainerResponseSerializer, PaperTradingResponseSerializer,
    InvestmentPlanResponseSerializer
)
from .signals_service import (
    MarketStatusService, SignalEnhancementService, SignalErrorHandler,
    SignalResponseFormatter, SignalDataValidator, SignalGenerationAwareService
)
from .services import (
    TechnicalAnalysisService, RiskManagementService,
    TradeRecommendationService, AlternativeInvestmentService,
    MarketSessionService, SignalGenerationService, RiskAnalyzerService,
    MarketSummaryService, TradingMistakeDetectorService, AIExplainerService,
    PaperTradingService, InvestmentPlannerService, StockRecommendationService,
    PatternScannerService, StockAnalysisService
)
from .stock_universe import StockUniverseManager
from .technical_analysis import (
    CandlestickPatternDetector, ChartPatternDetector,
    IndicatorCalculator, TradingLevelCalculator
)
from .pattern_scanner_service import (
    PatternScannerService, EnhancedCandlestickDetector,
    EnhancedChartPatternDetector, EnhancedIndicatorCalculator
)


class StockAnalysisViewSet(viewsets.ModelViewSet):
    """Stock Analysis endpoints"""
    
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [AllowAny]
    lookup_field = 'symbol'
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, symbol=None):
        """Analyze stock with technical indicators"""
        stock = self.get_object()
        
        # This would connect to real data source
        # For now, we'll create mock analysis
        
        try:
            analysis = stock.analysis
        except:
            return Response(
                {'error': 'No analysis data available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StockAnalysisSerializer(analysis)
        return Response(serializer.data)


class TradeRecommendationViewSet(viewsets.ModelViewSet):
    """Trade Recommendation endpoints"""
    
    queryset = TradeRecommendation.objects.all()
    serializer_class = TradeRecommendationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle POST to generate recommendation"""
        return self.generate(request)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate trade recommendation for a stock"""
        
        stock_symbol = request.data.get('stock_symbol')
        trading_style = request.data.get('trading_style', 'SWING')
        capital = Decimal(str(request.data.get('capital', 100000)))
        
        try:
            stock = Stock.objects.get(symbol=stock_symbol)
        except Stock.DoesNotExist:
            return Response(
                {'error': 'Stock not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            analysis = stock.analysis
        except:
            return Response(
                {'error': 'Analysis data not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate recommendation
        rec_data = TradeRecommendationService.generate_recommendation(
            stock, analysis, trading_style, capital
        )
        
        if not rec_data:
            return Response(
                {'error': 'Could not generate recommendation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create recommendation object
        recommendation = TradeRecommendation.objects.create(
            stock=stock,
            analysis=analysis,
            trading_style=trading_style,
            signal=rec_data['signal'],
            entry_price=rec_data['entry_price'],
            stop_loss=rec_data['stop_loss'],
            target_1=rec_data['targets'][0],
            target_2=rec_data['targets'][1] if len(rec_data['targets']) > 1 else None,
            target_3=rec_data['targets'][2] if len(rec_data['targets']) > 2 else None,
            target_4=rec_data['targets'][3] if len(rec_data['targets']) > 3 else None,
            risk_percent=rec_data['risk_percent'],
            profit_percent=rec_data['profit_percent'],
            risk_reward_ratio=rec_data['risk_reward_ratio'],
            confidence_level=rec_data['confidence'],
            win_probability=rec_data['win_probability']
        )
        
        # Create risk assessment
        risk_level = RiskManagementService.assess_risk_level(rec_data['risk_percent'])
        
        RiskAssessment.objects.create(
            recommendation=recommendation,
            risk_level=risk_level,
            risk_percentage=rec_data['risk_percent'],
            volatility_score=float(analysis.rsi),
            liquidity_score=90.0,
            market_condition_score=float(analysis.trend_probability),
            max_position_size=rec_data['quantity'],
            recommended_stop_loss=recommendation.stop_loss,
            assessment_notes=f"Risk controlled trade with {rec_data['risk_percent']:.2f}% risk"
        )
        
        # Add alternatives
        alternatives = AlternativeInvestmentService.get_alternatives(
            rec_data['signal'], trading_style
        )
        for alt in alternatives:
            AlternativeInvestment.objects.create(
                recommendation=recommendation,
                name=alt['name'],
                investment_type=alt['type'],
                description=f"{alt['name']} - {alt['type']} investment",
                expected_return=alt['expected_return'],
                risk_level=alt['risk'],
                liquidity=alt['liquidity'],
                reason=f"Alternative to {stock.symbol} with similar risk profile"
            )
        
        serializer = TradeRecommendationSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active recommendations with market awareness"""
        try:
            active = self.get_queryset().filter(signal__in=['BUY', 'SELL'])
            serializer = self.get_serializer(active, many=True)
            
            # Get market status
            market_open = MarketStatusService.is_market_open()
            market_status = MarketStatusService.get_market_status()
            
            # Enhance signals with market awareness
            signals_data = serializer.data
            enhanced_signals = [
                SignalEnhancementService.enhance_signal(sig, market_open)
                for sig in signals_data
            ]
            
            return Response(
                SignalResponseFormatter.format_signal_list(
                    enhanced_signals, market_open, len(active)
                )
            )
        except Exception as e:
            return Response(
                SignalResponseFormatter.format_error_response(e),
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute trade order from recommendation"""
        recommendation = self.get_object()
        
        quantity = int(request.data.get('quantity', 10))
        actual_price = Decimal(str(request.data.get('actual_price', recommendation.entry_price)))
        
        order = TradeOrder.objects.create(
            recommendation=recommendation,
            stock=recommendation.stock,
            quantity=quantity,
            entry_price=recommendation.entry_price,
            actual_entry_price=actual_price,
            stop_loss=recommendation.stop_loss,
            target=recommendation.target_1,
            capital_allocated=actual_price * quantity,
            risk_amount=recommendation.stop_loss * quantity
        )
        
        serializer = TradeOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PortfolioViewSet(viewsets.ModelViewSet):
    """Portfolio Management endpoints"""
    
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get portfolio summary"""
        portfolio = self.get_object()
        
        return Response({
            'portfolio': PortfolioSerializer(portfolio).data,
            'total_capital': float(portfolio.total_capital),
            'available_capital': float(portfolio.available_capital),
            'invested_capital': float(portfolio.invested_capital),
            'current_value': float(portfolio.current_value),
            'total_profit_loss': float(portfolio.total_profit_loss),
            'return_percent': float(
                (portfolio.total_profit_loss / portfolio.total_capital * 100)
                if portfolio.total_capital > 0 else 0
            )
        })
    
    @action(detail=True, methods=['post'])
    def add_capital(self, request, pk=None):
        """Add capital to portfolio"""
        portfolio = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        
        portfolio.total_capital += amount
        portfolio.available_capital += amount
        portfolio.save()
        
        return Response(PortfolioSerializer(portfolio).data)


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """Risk Assessment endpoints"""
    
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def assess(self, request):
        """Assess risk for a potential trade"""
        
        entry_price = Decimal(str(request.data.get('entry_price')))
        stop_loss = Decimal(str(request.data.get('stop_loss')))
        target_price = Decimal(str(request.data.get('target_price')))
        capital = Decimal(str(request.data.get('capital', 100000)))
        
        # Calculate risk metrics
        quantity = RiskManagementService.calculate_quantity(
            capital, entry_price, stop_loss
        )
        
        risk_amount = quantity * float(abs(entry_price - stop_loss))
        risk_percent = (risk_amount / float(capital)) * 100 if capital > 0 else 0
        
        risk_level = RiskManagementService.assess_risk_level(risk_percent)
        
        rr_ratio = RiskManagementService.calculate_risk_reward_ratio(
            entry_price, stop_loss, target_price
        )
        
        return Response({
            'quantity': quantity,
            'risk_amount': float(risk_amount),
            'risk_percent': risk_percent,
            'risk_level': risk_level,
            'risk_reward_ratio': rr_ratio,
            'capital_allocation': float(entry_price * quantity),
            'assessment': {
                'buy': risk_percent < 1.0,
                'max_position_size': quantity,
                'recommended_stop_loss': float(stop_loss),
                'probability_of_profit': rr_ratio > 1.0
            }
        })

# New Advanced Feature ViewSets

class SignalGenerationViewSet(viewsets.ViewSet):
    """Trading signal generation with Beginner/Pro modes"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def beginner_signal(self, request):
        """Generate simple Beginner Mode signals"""
        stock_symbol = request.data.get('symbol')
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        analysis = get_object_or_404(StockAnalysis, stock=stock)
        
        signal = SignalGenerationService.generate_beginner_signal(analysis)
        serializer = SignalResponseSerializer(signal)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def pro_signal(self, request):
        """Generate detailed Pro Mode signals with all indicators"""
        stock_symbol = request.data.get('symbol')
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        analysis = get_object_or_404(StockAnalysis, stock=stock)
        
        signal = SignalGenerationService.generate_pro_signal(analysis)
        return Response(signal)


class RiskAnalysisViewSet(viewsets.ViewSet):
    """Advanced risk analysis with capital checks"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def analyze_trade_risk(self, request):
        """Analyze risk with automatic capital checks and warnings"""
        
        portfolio_id = request.data.get('portfolio_id')
        stock_symbol = request.data.get('symbol')
        entry_price = Decimal(str(request.data.get('entry_price')))
        stop_loss = Decimal(str(request.data.get('stop_loss')))
        quantity = int(request.data.get('quantity', 1))
        
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        
        capital_available = portfolio.available_capital
        
        risk_analysis = RiskAnalyzerService.analyze_risk(
            portfolio, stock, entry_price, stop_loss, quantity, capital_available
        )
        
        serializer = RiskAnalysisResponseSerializer(risk_analysis)
        return Response(serializer.data)


class MarketSummaryViewSet(viewsets.ViewSet):
    """Daily market summary with sentiment analysis"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def today_summary(self, request):
        """Get today's market summary"""
        today = datetime.now().date()
        summary = get_object_or_404(MarketSummary, market_date=today)
        serializer = MarketSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_summary(self, request):
        """Generate market summary based on data"""
        
        gainers = request.data.get('gainers_count', 0)
        losers = request.data.get('losers_count', 0)
        sector_performance = request.data.get('sector_performance', {})
        volatility = request.data.get('volatility', None)
        
        summary = MarketSummaryService.generate_summary(
            gainers, losers, sector_performance, volatility
        )
        
        serializer = MarketSummaryResponseSerializer(summary)
        return Response(serializer.data)


class PortfolioHealthViewSet(viewsets.ModelViewSet):
    """Portfolio health analysis"""
    
    queryset = PortfolioHealth.objects.all()
    serializer_class = PortfolioHealthSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def portfolio_health(self, request):
        """Get health analysis for portfolio"""
        portfolio_id = request.query_params.get('portfolio_id')
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        health = get_object_or_404(PortfolioHealth, portfolio=portfolio)
        serializer = PortfolioHealthSerializer(health)
        return Response(serializer.data)


class TradingMistakeDetectorViewSet(viewsets.ViewSet):
    """Detect and learn from trading mistakes"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def analyze_mistake(self, request):
        """Analyze completed trade for mistakes"""
        
        entry_price = Decimal(str(request.data.get('entry_price')))
        exit_price = Decimal(str(request.data.get('exit_price')))
        stop_loss = Decimal(str(request.data.get('stop_loss')))
        quantity = int(request.data.get('quantity'))
        capital = Decimal(str(request.data.get('capital')))
        rsi_at_entry = float(request.data.get('rsi_at_entry', 50))
        holding_time = int(request.data.get('holding_time', 60))  # minutes
        is_loss = exit_price < entry_price
        previous_was_loss = request.data.get('previous_was_loss', False)
        
        mistakes = TradingMistakeDetectorService.analyze_trade(
            entry_price, exit_price, stop_loss, quantity, capital,
            rsi_at_entry, holding_time, is_loss, previous_was_loss
        )
        
        return Response({'mistakes': mistakes, 'count': len(mistakes)})


class AIExplainerViewSet(viewsets.ViewSet):
    """AI explanations for transparency"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def explain_signal(self, request):
        """Explain why a signal was generated"""
        
        stock_symbol = request.data.get('symbol')
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        analysis = get_object_or_404(StockAnalysis, stock=stock)
        
        # Determine signal
        if analysis.trend in ['BULLISH', 'STRONG_BULLISH'] and analysis.rsi < 50:
            signal = 'BUY'
        elif analysis.trend in ['BEARISH', 'STRONG_BEARISH'] and analysis.rsi > 50:
            signal = 'SELL'
        else:
            signal = 'HOLD'
        
        explanation = AIExplainerService.explain_signal(analysis, signal)
        serializer = AIExplainerResponseSerializer(explanation)
        return Response(serializer.data)


class PaperTradingViewSet(viewsets.ModelViewSet):
    """Paper trading with live market data and risk management"""
    
    queryset = PaperTrade.objects.all()
    serializer_class = PaperTradeSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def create_paper_trade(self, request):
        """Create a paper trade with live price validation and risk management"""
        
        try:
            portfolio_id = request.data.get('portfolio_id')
            stock_symbol = request.data.get('symbol')
            side = request.data.get('side', 'BUY')
            entry_price = Decimal(str(request.data.get('entry_price')))
            quantity = int(request.data.get('quantity'))
            stop_loss = Decimal(str(request.data.get('stop_loss')))
            capital = Decimal(str(request.data.get('capital', 100000)))
            
            # Optional targets
            target_1 = Decimal(str(request.data.get('target_1'))) if request.data.get('target_1') else None
            target_2 = Decimal(str(request.data.get('target_2'))) if request.data.get('target_2') else None
            target_3 = Decimal(str(request.data.get('target_3'))) if request.data.get('target_3') else None
            target_4 = Decimal(str(request.data.get('target_4'))) if request.data.get('target_4') else None
            
            portfolio = get_object_or_404(Portfolio, id=portfolio_id)
            stock = get_object_or_404(Stock, symbol=stock_symbol)
            
            result = PaperTradingService.create_paper_trade(
                portfolio=portfolio,
                stock=stock,
                side=side,
                entry_price=entry_price,
                quantity=quantity,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                target_3=target_3,
                target_4=target_4,
                capital=capital
            )
            
            if result['success']:
                serializer = PaperTradeSerializer(result['trade'])
                return Response({
                    'success': True,
                    'trade': serializer.data,
                    'validation': result['validation'],
                    'warnings': result['warnings']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'validation': result['validation'],
                    'errors': result['errors'],
                    'warnings': result['warnings']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def close_paper_trade(self, request, pk=None):
        """Close a paper trade with live price and P&L calculation"""
        
        try:
            paper_trade = self.get_object()
            exit_price = Decimal(str(request.data.get('exit_price'))) if request.data.get('exit_price') else None
            exit_type = request.data.get('exit_type', 'MANUAL')
            
            result = PaperTradingService.close_paper_trade(
                paper_trade=paper_trade,
                exit_price=exit_price,
                exit_type=exit_type
            )
            
            if result['success']:
                serializer = PaperTradeSerializer(result['trade'])
                return Response({
                    'success': True,
                    'trade': serializer.data,
                    'result': result['result']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to close trade')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active_trades(self, request):
        """Get all active paper trades with live prices"""
        try:
            portfolio_id = request.query_params.get('portfolio_id')
            portfolio = get_object_or_404(Portfolio, id=portfolio_id)
            
            # Update live prices
            PaperTradingService.update_live_prices(portfolio)
            
            trades = PaperTrade.objects.filter(portfolio=portfolio, status='ACTIVE')
            serializer = PaperTradeSerializer(trades, many=True)
            
            return Response({
                'success': True,
                'trades': serializer.data,
                'count': trades.count()
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def closed_trades(self, request):
        """Get all closed paper trades"""
        try:
            portfolio_id = request.query_params.get('portfolio_id')
            portfolio = get_object_or_404(Portfolio, id=portfolio_id)
            
            trades = PaperTrade.objects.filter(portfolio=portfolio, status='CLOSED')
            serializer = PaperTradeSerializer(trades, many=True)
            
            return Response({
                'success': True,
                'trades': serializer.data,
                'count': trades.count()
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get paper trading statistics"""
        try:
            portfolio_id = request.query_params.get('portfolio_id')
            portfolio = get_object_or_404(Portfolio, id=portfolio_id)
            
            stats = PaperTradingService.get_portfolio_stats(portfolio)
            
            return Response({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def sync_prices(self, request):
        """Manually sync live prices for a portfolio"""
        try:
            portfolio_id = request.data.get('portfolio_id')
            portfolio = get_object_or_404(Portfolio, id=portfolio_id)
            
            result = PaperTradingService.update_live_prices(portfolio)
            
            return Response({
                'success': True,
                'updated': result['updated'],
                'skipped': result['skipped'],
                'errors': result['errors']
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Get paper trading performance statistics"""
        portfolio_id = request.query_params.get('portfolio_id')
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        trades = PaperTrade.objects.filter(portfolio=portfolio, status='CLOSED')
        
        if not trades.exists():
            return Response({'error': 'No closed trades'}, status=status.HTTP_404_NOT_FOUND)
        
        total_trades = trades.count()
        winning_trades = trades.filter(profit_loss__gt=0).count()
        losing_trades = trades.filter(profit_loss__lt=0).count()
        
        total_profit_loss = sum(t.profit_loss for t in trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return Response({
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate_percent': win_rate,
            'total_profit_loss': float(total_profit_loss),
            'average_profit_per_trade': float(total_profit_loss / total_trades) if total_trades > 0 else 0
        })


class SmartAlertViewSet(viewsets.ModelViewSet):
    """Smart alerts for price, volume, and trend changes"""
    
    queryset = SmartAlert.objects.all()
    serializer_class = SmartAlertSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def create_alert(self, request):
        """Create a smart alert"""
        
        stock_symbol = request.data.get('symbol')
        alert_type = request.data.get('alert_type')
        target_value = float(request.data.get('target_value'))
        
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        
        alert = SmartAlert.objects.create(
            stock=stock,
            alert_type=alert_type,
            condition=request.data.get('condition', ''),
            target_value=target_value,
            send_email=request.data.get('send_email', True),
            send_notification=request.data.get('send_notification', True)
        )
        
        serializer = SmartAlertSerializer(alert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """Get all active alerts"""
        alerts = SmartAlert.objects.filter(status='ACTIVE')
        serializer = SmartAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def trigger_alert(self, request, pk=None):
        """Mark alert as triggered"""
        alert = self.get_object()
        alert.status = 'TRIGGERED'
        alert.triggered_at = datetime.now()
        alert.trigger_value = float(request.data.get('trigger_value'))
        alert.save()
        
        serializer = SmartAlertSerializer(alert)
        return Response(serializer.data)


class InvestmentPlannerViewSet(viewsets.ModelViewSet):
    """Investment planning based on user goals"""
    
    queryset = InvestmentPlan.objects.all()
    serializer_class = InvestmentPlanSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def create_plan(self, request):
        """Create an investment plan"""
        
        portfolio_id = request.data.get('portfolio_id')
        goal = request.data.get('goal')
        target_amount = Decimal(str(request.data.get('target_amount')))
        time_horizon = request.data.get('time_horizon')
        risk_tolerance = request.data.get('risk_tolerance', 'MEDIUM')
        
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        
        # Generate plan using service
        plan_data = InvestmentPlannerService.create_investment_plan(
            goal, target_amount, time_horizon, risk_tolerance
        )
        
        # Save to database
        plan = InvestmentPlan.objects.create(
            portfolio=portfolio,
            goal=goal,
            target_amount=target_amount,
            time_horizon=time_horizon,
            risk_tolerance=risk_tolerance,
            equity_percent=plan_data['allocation']['equity'],
            debt_percent=plan_data['allocation']['debt'],
            alternatives_percent=plan_data['allocation']['alternatives'],
            expected_returns=plan_data['expected_annual_return'],
            recommended_stocks=plan_data['recommended_stocks'],
            plan_description=plan_data['description']
        )
        
        serializer = InvestmentPlanResponseSerializer(plan_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def portfolio_plans(self, request):
        """Get all plans for a portfolio"""
        portfolio_id = request.query_params.get('portfolio_id')
        portfolio = get_object_or_404(Portfolio, id=portfolio_id)
        plans = InvestmentPlan.objects.filter(portfolio=portfolio)
        serializer = InvestmentPlanSerializer(plans, many=True)
        return Response(serializer.data)


class IntradaySignalViewSet(viewsets.ModelViewSet):
    """Intraday quick signals using VWAP, volume, and market timing"""
    
    permission_classes = [AllowAny]
    queryset = TradeRecommendation.objects.filter(trading_style='INTRADAY')
    serializer_class = TradeRecommendationSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle POST to generate intraday signal"""
        return self.generate_intraday(request)
    
    def list(self, request, *args, **kwargs):
        """Get intraday signals with market awareness"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            # Get market status
            market_open = MarketStatusService.is_market_open()
            
            # Enhance signals with market awareness
            signals_data = serializer.data
            enhanced_signals = [
                SignalEnhancementService.enhance_signal(sig, market_open)
                for sig in signals_data
            ]
            
            return Response(
                SignalResponseFormatter.format_signal_list(
                    enhanced_signals, market_open, len(queryset)
                )
            )
        except Exception as e:
            return Response(
                SignalResponseFormatter.format_error_response(e),
                status=status.HTTP_200_OK
            )
    
    @action(detail=False, methods=['post'])
    def generate_intraday(self, request):
        """Generate comprehensive intraday signal with proper price handling"""
        
        stock_symbol = request.data.get('stock_symbol')
        capital = Decimal(str(request.data.get('capital', 100000)))
        
        try:
            # Fetch live market data
            from .market_data import MarketDataFetcher
            
            stock = Stock.objects.get(symbol=stock_symbol)
            analysis = stock.analysis
            
            # Get LIVE price data
            live_data = MarketDataFetcher.get_stock_price(stock_symbol)
            if not live_data:
                return Response(
                    {'error': 'Failed to fetch live price data'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            current_price = Decimal(str(live_data['price']))
            previous_close = Decimal(str(live_data['previous_close']))
            
            # Intraday-specific technical analysis
            signal_data = SignalGenerationService.generate_intraday_signal(
                stock=stock,
                analysis=analysis,
                current_price=current_price,
                live_data=live_data,
                capital=capital
            )
            
            if not signal_data:
                return Response(
                    {'error': 'Could not generate intraday signal'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create recommendation with intraday-only settings
            recommendation = TradeRecommendation.objects.create(
                stock=stock,
                analysis=analysis,
                trading_style='INTRADAY',
                signal=signal_data['signal'],
                entry_price=signal_data['entry_price'],
                stop_loss=signal_data['stop_loss'],
                target_1=signal_data['targets'][0],
                target_2=signal_data['targets'][1] if len(signal_data['targets']) > 1 else None,
                target_3=signal_data['targets'][2] if len(signal_data['targets']) > 2 else None,
                target_4=signal_data['targets'][3] if len(signal_data['targets']) > 3 else None,
                risk_percent=signal_data['risk_percent'],
                profit_percent=signal_data['profit_percent'],
                risk_reward_ratio=signal_data['risk_reward_ratio'],
                confidence_level=signal_data['confidence'],
                win_probability=signal_data['win_probability'],
                valid_until_session=signal_data.get('valid_until', 'End of Day')
            )
            
            # Enhanced risk assessment for intraday
            risk_level = RiskManagementService.assess_risk_level(signal_data['risk_percent'])
            
            # Get validation results
            validation = signal_data.get('validation', {'valid': True, 'errors': [], 'warnings': []})
            
            RiskAssessment.objects.create(
                recommendation=recommendation,
                risk_level=risk_level,
                risk_percentage=signal_data['risk_percent'],
                volatility_score=float(analysis.rsi),
                liquidity_score=95.0,  # Intraday focuses on liquid stocks
                market_condition_score=float(analysis.trend_probability),
                max_position_size=signal_data['quantity'],
                recommended_stop_loss=recommendation.stop_loss,
                assessment_notes=f"INTRADAY - Auto square-off at market close. Risk: {signal_data['risk_percent']:.2f}%. "
                                f"Validation: {'✅ Passed' if validation['valid'] else '❌ Failed'}"
            )
            
            # Return response with validation
            response_data = {
                'id': recommendation.id,
                'stock': stock_symbol,
                'signal': signal_data['signal'],
                'entry_price': float(signal_data['entry_price']),
                'current_price': float(current_price),
                'previous_close': float(previous_close),
                'price_change': float(current_price - previous_close),
                'price_change_percent': float(((current_price - previous_close) / previous_close) * 100) if previous_close > 0 else 0,
                'stop_loss': float(signal_data['stop_loss']),
                'target_1': float(signal_data['targets'][0]),
                'target_2': float(signal_data['targets'][1] if len(signal_data['targets']) > 1 else 0),
                'target_3': float(signal_data['targets'][2] if len(signal_data['targets']) > 2 else 0),
                'target_4': float(signal_data['targets'][3] if len(signal_data['targets']) > 3 else 0),
                'risk_percent': signal_data['risk_percent'],
                'profit_percent': signal_data['profit_percent'],
                'risk_reward_ratio': signal_data['risk_reward_ratio'],
                'confidence_level': signal_data['confidence'],
                'win_probability': signal_data['win_probability'],
                'quantity': signal_data['quantity'],
                'capital_required': float(signal_data['quantity'] * signal_data['entry_price']),
                'technical_indicators': signal_data.get('indicators', {}),
                'market_data_freshness': live_data.get('data_freshness', 'LIVE'),
                'signal_timestamp': datetime.now().isoformat(),
                'valid_until_session': signal_data.get('valid_until', 'End of Day'),
                'auto_square_off': True,
                'validation': {
                    'valid': validation['valid'],
                    'errors': validation.get('errors', []),
                    'warnings': validation.get('warnings', [])
                }
            }
            
            # Only return if validation passed, else return as warning
            if not validation['valid']:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Stock.DoesNotExist:
            return Response(
                {'error': f'Stock {stock_symbol} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active_intraday(self, request):
        """Get all active intraday trades"""
        active = self.get_queryset().filter(signal__in=['BUY', 'SELL'])
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close_intraday(self, request, pk=None):
        """Close intraday trade with actual exit price"""
        recommendation = self.get_object()
        
        exit_price = Decimal(str(request.data.get('exit_price')))
        
        # Calculate actual P&L
        quantity = request.data.get('quantity', 1)
        entry = recommendation.entry_price
        actual_pnl = (exit_price - entry) * quantity
        actual_pnl_percent = float((actual_pnl / (entry * quantity)) * 100) if entry > 0 else 0
        
        return Response({
            'recommendation_id': recommendation.id,
            'stock': recommendation.stock.symbol,
            'entry_price': float(entry),
            'exit_price': float(exit_price),
            'quantity': quantity,
            'pnl': float(actual_pnl),
            'pnl_percent': actual_pnl_percent,
            'status': 'CLOSED',
            'closed_at': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute intraday trade order"""
        recommendation = self.get_object()
        
        quantity = int(request.data.get('quantity', 10))
        actual_price = Decimal(str(request.data.get('actual_price', recommendation.entry_price)))
        
        # Validate capital
        capital_required = quantity * actual_price
        capital = Decimal(str(request.data.get('capital', 100000)))
        
        if capital_required > capital:
            return Response(
                {'error': f'Insufficient capital. Required: ₹{capital_required}, Available: ₹{capital}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create intraday trade order with auto square-off
        from datetime import time
        order = TradeOrder.objects.create(
            recommendation=recommendation,
            stock=recommendation.stock,
            quantity=quantity,
            entry_price=recommendation.entry_price,
            actual_entry_price=actual_price,
            stop_loss=recommendation.stop_loss,
            target=recommendation.target_1,
            capital_allocated=actual_price * quantity,
            risk_amount=recommendation.stop_loss * quantity,
            # Intraday-specific
            is_intraday=True,
            auto_square_off=True,
            square_off_time=time(15, 30),  # 3:30 PM IST
            status='EXECUTED',
            entry_time=datetime.now()
        )
        
        serializer = TradeOrderSerializer(order)
        return Response({
            **serializer.data,
            'auto_square_off': True,
            'square_off_time': '15:30',  # 3:30 PM
            'message': 'Intraday trade executed. Will be automatically squared off at market close.'
        }, status=status.HTTP_201_CREATED)
        return Response({
            'recommendation_id': recommendation.id,
            'stock': recommendation.stock.symbol,
            'entry_price': float(entry),
            'exit_price': float(exit_price),
            'quantity': quantity,
            'pnl': float(actual_pnl),
            'pnl_percent': actual_pnl_percent,
            'status': 'CLOSED',
            'closed_at': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def quick_signal(self, request):
        """Generate quick intraday signal using VWAP, volume, EMA"""
        
        stock_symbol = request.data.get('symbol')
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        analysis = get_object_or_404(StockAnalysis, stock=stock)
        
        # Get live price
        from .market_data import MarketDataFetcher
        live_data = MarketDataFetcher.get_stock_price(stock_symbol)
        current_price = Decimal(str(live_data['price'])) if live_data else analysis.current_price
        
        # VWAP Signal
        price_vs_vwap = float(current_price) - float(analysis.vwap)
        vwap_signal = 'BULLISH' if price_vs_vwap > 0 else 'BEARISH'
        vwap_strength = abs(price_vs_vwap) / float(analysis.vwap) * 100
        
        # EMA Signals (12/26 crossover)
        ema_12 = float(analysis.ema_12) if analysis.ema_12 else float(current_price)
        ema_26 = float(analysis.ema_26) if analysis.ema_26 else float(current_price)
        ema_signal = 'BULLISH' if ema_12 > ema_26 else 'BEARISH'
        
        # Volume Signal
        volume_signal = 'STRONG' if analysis.volume > analysis.average_volume_20 * 1.3 else ('WEAK' if analysis.volume < analysis.average_volume_20 * 0.8 else 'NORMAL')
        
        # RSI Intraday Analysis
        if analysis.rsi < 30:
            rsi_signal = 'OVERSOLD - Buy opportunity'
        elif analysis.rsi > 70:
            rsi_signal = 'OVERBOUGHT - Sell opportunity'
        elif analysis.rsi < 50:
            rsi_signal = 'Bearish bias'
        else:
            rsi_signal = 'Bullish bias'
        
        # Combined strength
        bullish_count = sum([
            vwap_signal == 'BULLISH',
            ema_signal == 'BULLISH',
            'Buy' in rsi_signal or 'Bullish' in rsi_signal,
            volume_signal in ['STRONG', 'NORMAL']
        ])
        
        if bullish_count >= 3:
            action = 'BUY'
            action_strength = 'STRONG'
        elif bullish_count >= 2:
            action = 'BUY'
            action_strength = 'MODERATE'
        elif bullish_count == 1:
            action = 'HOLD'
            action_strength = 'WEAK'
        else:
            action = 'SELL'
            action_strength = 'STRONG' if volume_signal == 'STRONG' else 'MODERATE'
        
        return Response({
            'stock': stock_symbol,
            'current_price': float(current_price),
            'signal': action,
            'signal_strength': action_strength,
            'technical_indicators': {
                'vwap': {
                    'value': float(analysis.vwap),
                    'price_vs_vwap': float(price_vs_vwap),
                    'strength_percent': round(vwap_strength, 2),
                    'signal': vwap_signal
                },
                'ema': {
                    'ema_12': float(ema_12),
                    'ema_26': float(ema_26),
                    'signal': ema_signal
                },
                'volume': {
                    'current': analysis.volume,
                    'average_20': analysis.average_volume_20,
                    'signal': volume_signal
                },
                'rsi': {
                    'value': round(analysis.rsi, 2),
                    'signal': rsi_signal
                }
            },
            'recommendation': f'{action} - {action_strength} signal. VWAP: {vwap_signal}, EMA: {ema_signal}, Volume: {volume_signal}'
        })


class SupportResistanceViewSet(viewsets.ViewSet):
    """Auto calculate support and resistance levels"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def calculate_levels(self, request):
        """Calculate support and resistance levels"""
        
        stock_symbol = request.data.get('symbol')
        stock = get_object_or_404(Stock, symbol=stock_symbol)
        analysis = get_object_or_404(StockAnalysis, stock=stock)
        
        return Response({
            'stock': stock_symbol,
            'current_price': float(analysis.current_price),
            'support_levels': [
                float(analysis.support_level),
                float(analysis.support_level * 0.98),
                float(analysis.fib_0_618)
            ],
            'resistance_levels': [
                float(analysis.resistance_level),
                float(analysis.resistance_level * 1.02),
                float(analysis.fib_0_236)
            ],
            'fibonacci_levels': {
                '23.6%': float(analysis.fib_0_236),
                '38.2%': float(analysis.fib_0_382),
                '50%': float(analysis.fib_0_500),
                '61.8%': float(analysis.fib_0_618)
            }
        })


class TechnicalAnalysisViewSet(viewsets.ViewSet):
    """Comprehensive technical analysis with pattern detection"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def analyze_technical(self, request):
        """
        Enhanced technical analysis with real pattern detection
        Request: { "symbol": "INFY", "timeframe": "1D" }
        Returns: Complete analysis with candlestick/chart patterns, indicators, trading levels
        """
        
        stock_symbol = request.data.get('symbol', 'INFY').upper()
        timeframe = request.data.get('timeframe', '1D')
        
        try:
            stock = get_object_or_404(Stock, symbol=stock_symbol)
            analysis = get_object_or_404(StockAnalysis, stock=stock)
            
            # Get current price data from model
            current_price = float(analysis.current_price or 1500)
            high = float(analysis.resistance_level or current_price * 1.02)
            low = float(analysis.support_level or current_price * 0.98)
            open_price = (high + low) / 2  # Calculate from high/low if not available
            volume = float(analysis.volume or 1000000)
            
            # Generate synthetic historical data for demonstration (in production, use real historical data)
            # Create last 50 prices with realistic movement
            prices_history = [current_price]
            for i in range(49):
                # Create realistic price history
                change = (current_price * 0.02 * (0.5 - i/100))  # Gradual change
                prices_history.insert(0, max(current_price * 0.95, current_price - abs(change)))
            
            volumes_history = [volume * (0.8 + (i % 5) * 0.1) for i in range(50)]
            
            # Use enhanced pattern scanner service
            scan_result = PatternScannerService.scan_stock(
                current_price=current_price,
                high=high,
                low=low,
                open_price=open_price,
                volume=volume,
                prices_history=prices_history,
                volumes_history=volumes_history,
                prev_candle=None
            )
            
            # Format response with meaningful fallbacks
            response_data = {
                'stock': stock_symbol,
                'current_price': current_price,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'market_status': request.data.get('market_open', True),  # Will be set by frontend
                
                # Pattern data
                'candlestick_patterns': [
                    {
                        'name': p['name'],
                        'type': p['type'],
                        'signal': p['signal'],
                        'confidence': int(p.get('confidence', 65)),
                        'description': p.get('description', '')
                    }
                    for p in scan_result.get('candlestick_patterns', [])
                ],
                'chart_patterns': [
                    {
                        'pattern': p['pattern'],
                        'type': p['type'],
                        'signal': p['signal'],
                        'confidence': int(p.get('confidence', 65)),
                        'description': p.get('description', '')
                    }
                    for p in scan_result.get('chart_patterns', [])
                ],
                
                # Indicators
                'indicators': {
                    'rsi': float(scan_result['indicators'].get('rsi', 50)),
                    'vwap': float(scan_result['indicators'].get('vwap', current_price)),
                    'ema_20': float(scan_result['indicators'].get('ema_20', current_price)),
                    'ema_50': float(scan_result['indicators'].get('ema_50', current_price)),
                    'ema_100': float(scan_result['indicators'].get('ema_100', current_price)),
                    'ema_200': float(scan_result['indicators'].get('ema_200', current_price)),
                    'bollinger_bands': {
                        'upper': float(scan_result['indicators']['bollinger_bands'].get('upper', current_price * 1.02)),
                        'middle': float(scan_result['indicators']['bollinger_bands'].get('middle', current_price)),
                        'lower': float(scan_result['indicators']['bollinger_bands'].get('lower', current_price * 0.98)),
                    }
                },
                
                # Trading levels
                'trading_levels': {
                    'support': float(scan_result['trading_levels'].get('support', low)),
                    'resistance': float(scan_result['trading_levels'].get('resistance', high)),
                    'fibonacci': {
                        str(k): float(v) for k, v in scan_result['trading_levels'].get('fibonacci', {}).items()
                    }
                },
                
                # Entry/Exit
                'entry_exit': {
                    'entry_points': float(scan_result['entry_exit'].get('entry', current_price)),
                    'targets': {
                        'target_1': float(scan_result['entry_exit'].get('target_1', current_price * 1.02)),
                        'target_2': float(scan_result['entry_exit'].get('target_2', current_price * 1.05)),
                        'target_3': float(scan_result['entry_exit'].get('target_3', current_price * 1.08)),
                        'target_4': float(scan_result['entry_exit'].get('target_4', current_price * 1.10)),
                    },
                    'stop_loss': float(scan_result['entry_exit'].get('stop_loss', current_price * 0.98))
                },
                
                # Summary
                'summary': scan_result.get('summary', {
                    'total_patterns': 0,
                    'bullish_signals': 0,
                    'bearish_signals': 0,
                    'overall_sentiment': 'NEUTRAL',
                    'confidence': 50
                })
            }
            
            return Response(response_data)
            
        except Stock.DoesNotExist:
            return Response(
                {'error': f'Stock "{stock_symbol}" not found. Available: INFY, TCS, HDFCBANK'},
                status=status.HTTP_404_NOT_FOUND
            )
        except StockAnalysis.DoesNotExist:
            return Response(
                {'error': f'Analysis data not available for {stock_symbol}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Technical analysis failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DynamicStockRecommendationViewSet(viewsets.ViewSet):
    """Dynamic stock recommendations using full NSE & BSE universe"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def get_recommendations(self, request):
        """
        Get stock recommendations by category
        
        Request body:
        {
            'market': 'NSE',  # NSE, BSE, ALL
            'category': 'large_cap',  # large_cap, mid_cap, high_dividend, gainers
            'limit': 10,
            'sector': null
        }
        """
        
        try:
            market = request.data.get('market', 'NSE')
            category = request.data.get('category', 'large_cap')
            limit = request.data.get('limit', 10)
            sector = request.data.get('sector', None)
            
            recommendations = StockRecommendationService.get_recommendations(
                market=market,
                category=category,
                limit=limit,
                sector=sector
            )
            
            return Response({
                'status': 'success',
                'category': category,
                'market': market,
                'total': len(recommendations),
                'stocks': recommendations
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get recommendations: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def get_sector_recommendations(self, request):
        """
        Get top stocks in a specific sector
        
        Request body:
        {
            'sector': 'Banking',
            'market': 'NSE',
            'limit': 10,
            'sort_by': 'market_cap'
        }
        """
        
        try:
            sector = request.data.get('sector')
            market = request.data.get('market', 'NSE')
            limit = request.data.get('limit', 10)
            sort_by = request.data.get('sort_by', 'market_cap')
            
            if not sector:
                return Response(
                    {'error': 'Sector is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stocks = StockRecommendationService.get_sector_recommendations(
                sector=sector,
                market=market,
                limit=limit,
                sort_by=sort_by
            )
            
            return Response({
                'status': 'success',
                'sector': sector,
                'total': len(stocks),
                'stocks': stocks
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get sector recommendations: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def get_all_sectors(self, request):
        """Get all available sectors"""
        
        try:
            market = request.query_params.get('market', 'NSE')
            sectors = StockRecommendationService.get_all_sectors(market)
            
            return Response({
                'status': 'success',
                'market': market,
                'total': len(sectors),
                'sectors': sectors
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get sectors: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search for stocks
        
        Request body:
        {
            'query': 'INFY',
            'market': 'NSE',
            'limit': 10
        }
        """
        
        try:
            query = request.data.get('query', '')
            market = request.data.get('market', 'NSE')
            limit = request.data.get('limit', 10)
            
            if not query:
                return Response(
                    {'error': 'Search query is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = StockRecommendationService.search_recommendations(
                query=query,
                market=market,
                limit=limit
            )
            
            return Response({
                'status': 'success',
                'query': query,
                'total': len(results),
                'stocks': results
            })
            
        except Exception as e:
            return Response(
                {'error': f'Search failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class StockScannerViewSet(viewsets.ViewSet):
    """Dynamic stock scanner with multiple scanning strategies"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def scan_breakouts(self, request):
        """
        Scan for breakout candidates
        
        Request body:
        {
            'market': 'NSE',
            'sector': null,
            'limit': 10
        }
        """
        
        try:
            market = request.data.get('market', 'NSE')
            sector = request.data.get('sector', None)
            limit = request.data.get('limit', 10)
            
            stocks = PatternScannerService.scan_for_breakouts(
                market=market,
                sector=sector,
                limit=limit
            )
            
            return Response({
                'status': 'success',
                'scan_type': 'breakouts',
                'total': len(stocks),
                'stocks': stocks
            })
            
        except Exception as e:
            return Response(
                {'error': f'Breakout scan failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def scan_reversals(self, request):
        """
        Scan for reversal candidates
        
        Request body:
        {
            'market': 'NSE',
            'sector': null,
            'limit': 10
        }
        """
        
        try:
            market = request.data.get('market', 'NSE')
            sector = request.data.get('sector', None)
            limit = request.data.get('limit', 10)
            
            stocks = PatternScannerService.scan_for_reversals(
                market=market,
                sector=sector,
                limit=limit
            )
            
            return Response({
                'status': 'success',
                'scan_type': 'reversals',
                'total': len(stocks),
                'stocks': stocks
            })
            
        except Exception as e:
            return Response(
                {'error': f'Reversal scan failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def scan_dividends(self, request):
        """
        Scan for dividend stocks
        
        Request body:
        {
            'market': 'NSE',
            'min_yield': 0.02,
            'limit': 10
        }
        """
        
        try:
            market = request.data.get('market', 'NSE')
            min_yield = float(request.data.get('min_yield', 0.02))
            limit = request.data.get('limit', 10)
            
            stocks = PatternScannerService.scan_dividend_stocks(
                market=market,
                min_yield=min_yield,
                limit=limit
            )
            
            return Response({
                'status': 'success',
                'scan_type': 'dividend_stocks',
                'total': len(stocks),
                'stocks': stocks
            })
            
        except Exception as e:
            return Response(
                {'error': f'Dividend scan failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def scan_custom(self, request):
        """
        Scan stocks with custom criteria
        
        Request body:
        {
            'market': 'NSE',
            'sector': null,
            'min_price': null,
            'max_price': null,
            'min_market_cap': null,
            'min_volume': null,
            'limit': 10
        }
        """
        
        try:
            market = request.data.get('market', 'NSE')
            sector = request.data.get('sector', None)
            min_price = request.data.get('min_price', None)
            max_price = request.data.get('max_price', None)
            min_market_cap = request.data.get('min_market_cap', None)
            min_volume = request.data.get('min_volume', None)
            limit = request.data.get('limit', 10)
            
            stocks = PatternScannerService.scan_by_criteria(
                market=market,
                sector=sector,
                min_price=min_price,
                max_price=max_price,
                min_market_cap=min_market_cap,
                min_volume=min_volume,
                limit=limit
            )
            
            return Response({
                'status': 'success',
                'scan_type': 'custom',
                'criteria': {
                    'market': market,
                    'sector': sector,
                    'price_range': (min_price, max_price),
                    'min_market_cap': min_market_cap,
                    'min_volume': min_volume
                },
                'total': len(stocks),
                'stocks': stocks
            })
            
        except Exception as e:
            return Response(
                {'error': f'Custom scan failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def sector_performance(self, request):
        """
        Get top performers in each sector
        
        Query params:
        ?market=NSE
        """
        
        try:
            market = request.query_params.get('market', 'NSE')
            
            sector_perf = PatternScannerService.scan_sector_performance(market)
            
            return Response({
                'status': 'success',
                'market': market,
                'sectors': len(sector_perf),
                'data': sector_perf
            })
            
        except Exception as e:
            return Response(
                {'error': f'Sector performance scan failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DynamicStockAnalysisViewSet(viewsets.ViewSet):
    """Dynamic stock analysis using full universe data"""
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def get_stock_profile(self, request):
        """
        Get complete stock profile
        
        Request body:
        {
            'symbol': 'INFY',
            'market': 'NSE'
        }
        """
        
        try:
            symbol = request.data.get('symbol', '').upper()
            market = request.data.get('market', 'NSE')
            
            if not symbol:
                return Response(
                    {'error': 'Symbol is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            profile = StockAnalysisService.get_stock_profile(symbol, market)
            
            return Response({
                'status': 'success',
                'symbol': symbol,
                'profile': profile
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get stock profile: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def compare_stocks(self, request):
        """
        Compare multiple stocks
        
        Request body:
        {
            'symbols': ['INFY', 'TCS', 'WIPRO'],
            'market': 'NSE'
        }
        """
        
        try:
            symbols = request.data.get('symbols', [])
            market = request.data.get('market', 'NSE')
            
            if not symbols:
                return Response(
                    {'error': 'Symbols list is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            symbols = [s.upper() for s in symbols]
            
            comparison = StockAnalysisService.compare_stocks(symbols, market)
            
            return Response({
                'status': 'success',
                'total': len(comparison),
                'stocks': comparison
            })
            
        except Exception as e:
            return Response(
                {'error': f'Stock comparison failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def sector_analysis(self, request):
        """
        Get sector analysis with top stocks
        
        Request body:
        {
            'sector': 'Banking',
            'market': 'NSE'
        }
        """
        
        try:
            sector = request.data.get('sector')
            market = request.data.get('market', 'NSE')
            
            if not sector:
                return Response(
                    {'error': 'Sector is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            analysis = StockAnalysisService.get_sector_analysis(sector, market)
            
            return Response({
                'status': 'success',
                'sector': sector,
                'analysis': analysis
            })
            
        except Exception as e:
            return Response(
                {'error': f'Sector analysis failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def universe_stats(self, request):
        """
        Get stock universe statistics
        
        Query params:
        ?market=NSE
        """
        
        try:
            market = request.query_params.get('market', 'NSE')
            
            stocks = StockUniverseManager.get_all_stocks(market)
            sectors = StockUniverseManager.get_sectors(market)
            
            # Calculate statistics
            prices = [s.get('price', 0) for s in stocks.values() if s.get('price')]
            market_caps = [s.get('market_cap', 0) for s in stocks.values() if s.get('market_cap')]
            
            return Response({
                'status': 'success',
                'market': market,
                'statistics': {
                    'total_stocks': len(stocks),
                    'total_sectors': len(sectors),
                    'avg_price': sum(prices) / len(prices) if prices else 0,
                    'avg_market_cap': sum(market_caps) / len(market_caps) if market_caps else 0
                },
                'sectors': sectors
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get universe stats: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

