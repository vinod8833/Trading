"""
ViewSets for Market Data and AI Trading Signals
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta

from .models import (
    StockPriceSnapshot, MarketIndex, SectorPerformance,
    TradeSignal, SignalHistory, DataSource
)
from .market_serializers import (
    StockPriceSnapshotSerializer, MarketIndexSerializer, SectorPerformanceSerializer,
    TradeSignalSerializer, TradeSignalListSerializer, SignalHistorySerializer,
    DataSourceSerializer
)
from .market_data import MarketDataFetcher
from .ai_signals import AISignalGenerator


class StockPriceSnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for stock price snapshots
    
    Endpoints:
    - GET /api/market/prices/ - List price snapshots
    - GET /api/market/prices/{id}/ - Get price details
    - GET /api/market/prices/latest/ - Get latest price for symbol
    - POST /api/market/prices/fetch/ - Fetch latest prices
    """
    
    queryset = StockPriceSnapshot.objects.all()
    serializer_class = StockPriceSnapshotSerializer
    filterset_fields = ['symbol', 'data_freshness', 'market_status']
    ordering_fields = ['symbol', 'current_price', 'timestamp']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest price for a symbol"""
        symbol = request.query_params.get('symbol')
        if not symbol:
            return Response(
                {'error': 'Symbol parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            latest = StockPriceSnapshot.objects.filter(
                symbol=symbol
            ).latest('timestamp')
            serializer = self.get_serializer(latest)
            return Response(serializer.data)
        except StockPriceSnapshot.DoesNotExist:
            return Response(
                {'error': f'No price data for {symbol}'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def fetch(self, request):
        """Fetch latest prices from market data source"""
        symbols = request.data.get('symbols', [])
        
        if not symbols:
            return Response(
                {'error': 'Symbols list required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fetched = 0
        errors = []
        
        try:
            for symbol in symbols:
                try:
                    data = MarketDataFetcher.get_stock_price(symbol)
                    if data:
                        # Validate data quality
                        is_valid, validation_msg = MarketDataFetcher.validate_data_quality(data)
                        if is_valid:
                            StockPriceSnapshot.objects.create(
                                symbol=symbol,
                                current_price=data['price'],
                                previous_close=data['previous_close'],
                                open_price=data['open'],
                                high_price=data['high'],
                                low_price=data['low'],
                                volume=data['volume'],
                                market_cap=data.get('market_cap'),
                                pe_ratio=data.get('pe_ratio'),
                                data_source=data.get('source', 'yfinance'),
                                data_freshness=data.get('data_freshness', 'EOD'),
                                market_status=data.get('market_status', 'CLOSED'),
                            )
                            fetched += 1
                except Exception as e:
                    errors.append(f"{symbol}: {str(e)}")
            
            return Response({
                'status': 'success',
                'fetched': fetched,
                'total': len(symbols),
                'errors': errors
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's price data"""
        from datetime import date
        today = date.today()
        
        prices = StockPriceSnapshot.objects.filter(
            timestamp__date=today
        ).order_by('-timestamp')
        
        serializer = self.get_serializer(prices, many=True)
        return Response(serializer.data)


class MarketIndexViewSet(viewsets.ModelViewSet):
    """
    ViewSet for market indices
    
    Endpoints:
    - GET /api/market/indices/ - List indices
    - GET /api/market/indices/{id}/ - Get index details
    - POST /api/market/indices/fetch/ - Update indices
    """
    
    queryset = MarketIndex.objects.all()
    serializer_class = MarketIndexSerializer
    filterset_fields = ['index_name']
    
    @action(detail=False, methods=['post'])
    def fetch(self, request):
        """Fetch latest market indices"""
        try:
            indices_data = MarketDataFetcher.get_market_indices()
            
            fetched = 0
            for name, data in indices_data.items():
                try:
                    index_obj, created = MarketIndex.objects.update_or_create(
                        index_name=name,
                        defaults={
                            'symbol': name,
                            'current_value': data['value'],
                            'previous_close': data['value'] - data.get('change', 0),
                            'change_points': data.get('change', 0),
                            'change_percent': (data.get('change', 0) / (data['value'] - data.get('change', 0)) * 100)
                            if data['value'] != data.get('change', 0) else 0,
                        }
                    )
                    fetched += 1
                except Exception as e:
                    continue
            
            return Response({
                'status': 'success',
                'fetched': fetched,
                'message': f'Updated {fetched} indices'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SectorPerformanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for sector performance
    
    Endpoints:
    - GET /api/market/sectors/ - List sector performance
    - GET /api/market/sectors/{id}/ - Get sector details
    - POST /api/market/sectors/fetch/ - Update sector data
    """
    
    queryset = SectorPerformance.objects.all()
    serializer_class = SectorPerformanceSerializer
    filterset_fields = ['sector']
    
    @action(detail=False, methods=['post'])
    def fetch(self, request):
        """Fetch sector performance data"""
        try:
            sectors_data = MarketDataFetcher.get_sector_performance()
            
            fetched = 0
            for sector_name, data in sectors_data.items():
                try:
                    sector_obj, created = SectorPerformance.objects.update_or_create(
                        sector=sector_name,
                        defaults={
                            'index_symbol': f'NIFTY_{sector_name}',
                            'current_value': data['value'],
                            'change_percent': data.get('change_percent', 0),
                        }
                    )
                    fetched += 1
                except Exception as e:
                    continue
            
            return Response({
                'status': 'success',
                'fetched': fetched,
                'message': f'Updated {fetched} sectors'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TradeSignalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for trade signals
    
    Endpoints:
    - GET /api/signals/ - List all signals
    - GET /api/signals/{id}/ - Get signal details
    - POST /api/signals/generate/ - Generate new signal
    - GET /api/signals/latest/ - Get latest signals
    - GET /api/signals/by-type/ - Filter by signal type
    """
    
    queryset = TradeSignal.objects.all()
    filterset_fields = ['symbol', 'signal', 'data_quality']
    ordering_fields = ['confidence', 'symbol', 'generated_at']
    ordering = ['-generated_at']
    
    def get_serializer_class(self):
        """Use list serializer for list action"""
        if self.action == 'list':
            return TradeSignalListSerializer
        return TradeSignalSerializer
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate new trading signal"""
        symbol = request.data.get('symbol')
        
        if not symbol:
            return Response(
                {'error': 'Symbol required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Fetch historical data
            hist_data = MarketDataFetcher.get_historical_data(symbol, period='1y', interval='1d')
            
            if hist_data is None or hist_data.empty:
                return Response(
                    {'error': f'No historical data available for {symbol}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get current price
            current_data = MarketDataFetcher.get_stock_price(symbol)
            if not current_data:
                return Response(
                    {'error': f'Could not fetch current price for {symbol}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            current_price = current_data['price']
            
            # Prepare data for signal generation
            prices = hist_data['Close'].tolist()
            volumes = hist_data['Volume'].tolist()
            highs = hist_data['High'].tolist()
            lows = hist_data['Low'].tolist()
            
            # Generate signal
            signal_data = AISignalGenerator.generate_signal(
                symbol=symbol,
                prices=prices,
                volumes=volumes,
                highs=highs,
                lows=lows,
                current_price=current_price
            )
            
            # Save to database
            signal_obj = TradeSignal.objects.create(
                symbol=symbol,
                signal=signal_data['signal'],
                confidence=signal_data['confidence'],
                confidence_min=signal_data['confidence_range'][0],
                confidence_max=signal_data['confidence_range'][1],
                entry_price=signal_data['entry_price'],
                target_price=signal_data['target_price'],
                stop_loss=signal_data['stop_loss'],
                risk_reward_ratio=signal_data['risk_reward_ratio'],
                technical_patterns=signal_data['factors'].get('technical_patterns', []),
                volume_signal=signal_data['factors'].get('volume_signal', 'NEUTRAL'),
                trend=signal_data['factors'].get('trend', 'NEUTRAL'),
                momentum=signal_data['factors'].get('momentum', 'NEUTRAL'),
                volatility=signal_data['factors'].get('volatility', 'MODERATE'),
                uptrend_probability=signal_data['probability_analysis'].get('uptrend_probability', 0.5),
                breakout_probability=signal_data['probability_analysis'].get('breakout_probability', 0.5),
                support_hold_probability=signal_data['probability_analysis'].get('support_hold_probability', 0.5),
                warning_flags=signal_data['warning_flags'],
                data_quality=signal_data['data_quality'],
                confidence_reason=signal_data['confidence_reason'],
            )
            
            serializer = TradeSignalSerializer(signal_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest signals"""
        limit = int(request.query_params.get('limit', 10))
        
        signals = TradeSignal.objects.order_by('-generated_at')[:limit]
        serializer = TradeSignalListSerializer(signals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get signals by type"""
        signal_type = request.query_params.get('type', 'BUY')
        
        signals = TradeSignal.objects.filter(
            signal=signal_type
        ).order_by('-generated_at')
        
        serializer = TradeSignalListSerializer(signals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_confidence(self, request):
        """Get high confidence signals (>70%)"""
        signals = TradeSignal.objects.filter(
            confidence__gte=0.70
        ).order_by('-confidence', '-generated_at')
        
        serializer = TradeSignalListSerializer(signals, many=True)
        return Response(serializer.data)


class SignalHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for signal performance tracking
    
    Endpoints:
    - GET /api/signal-history/ - List all history
    - GET /api/signal-history/stats/ - Get accuracy statistics
    - GET /api/signal-history/by-symbol/ - Filter by symbol
    """
    
    queryset = SignalHistory.objects.all()
    serializer_class = SignalHistorySerializer
    filterset_fields = ['signal', 'exit_reason', 'signal_accuracy']
    ordering_fields = ['created_at', 'profit_loss_percent']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get signal accuracy statistics"""
        try:
            total = SignalHistory.objects.filter(exit_reason__in=['TARGET_HIT', 'STOP_LOSS_HIT']).count()
            
            if total == 0:
                return Response({
                    'total_signals': 0,
                    'message': 'No completed signals yet'
                })
            
            accurate = SignalHistory.objects.filter(
                exit_reason__in=['TARGET_HIT', 'STOP_LOSS_HIT'],
                signal_accuracy=True
            ).count()
            
            total_profit = SignalHistory.objects.filter(
                exit_reason__in=['TARGET_HIT', 'STOP_LOSS_HIT']
            ).aggregate(
                total_pl=models.F('profit_loss_rupees'),
            )
            
            avg_profit = SignalHistory.objects.filter(
                exit_reason__in=['TARGET_HIT', 'STOP_LOSS_HIT']
            ).aggregate(
                avg_pl=models.Avg('profit_loss_percent'),
            )
            
            return Response({
                'total_signals': total,
                'accurate_signals': accurate,
                'accuracy_percent': (accurate / total * 100) if total > 0 else 0,
                'total_profit_loss': total_profit['total_pl'] or 0,
                'avg_profit_loss_percent': avg_profit['avg_pl'] or 0,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_symbol(self, request):
        """Get history for specific symbol"""
        symbol = request.query_params.get('symbol')
        
        if not symbol:
            return Response(
                {'error': 'Symbol parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = SignalHistory.objects.filter(
            signal__symbol=symbol
        ).order_by('-created_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for data sources
    
    Endpoints:
    - GET /api/data-sources/ - List sources
    - GET /api/data-sources/{id}/ - Get source details
    - POST /api/data-sources/health/ - Check source health
    """
    
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    filterset_fields = ['is_free', 'is_available', 'provides_price']
    
    @action(detail=False, methods=['post'])
    def health(self, request):
        """Check health of data sources"""
        try:
            sources = DataSource.objects.all()
            health_status = {}
            
            for source in sources:
                # Simple health check - update last_checked timestamp
                source.last_checked = timezone.now()
                source.save()
                
                health_status[source.name] = {
                    'is_available': source.is_available,
                    'last_checked': source.last_checked.isoformat() if source.last_checked else None,
                }
            
            return Response({
                'status': 'success',
                'sources_checked': len(health_status),
                'health': health_status
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
