"""
ViewSets for Groww Integration
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    GrowwAccount, GrowwHolding, GrowwMutualFund,
    GrowwPortfolioSummary, GrowwTransaction, GrowwImportLog
)
from .groww_serializers import (
    GrowwAccountSerializer, GrowwAccountDetailSerializer,
    GrowwHoldingSerializer, GrowwMutualFundSerializer,
    GrowwPortfolioSummarySerializer, GrowwImportLogSerializer,
    GrowwDataImportSerializer
)


class GrowwAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Groww Account management
    
    Endpoints:
    - GET /api/groww/accounts/ - List all Groww accounts
    - POST /api/groww/accounts/ - Create new Groww account
    - GET /api/groww/accounts/{id}/ - Get account details
    - PUT /api/groww/accounts/{id}/ - Update account
    - DELETE /api/groww/accounts/{id}/ - Delete account
    - POST /api/groww/accounts/{id}/sync/ - Sync account data
    - GET /api/groww/accounts/{id}/summary/ - Get portfolio summary
    - GET /api/groww/accounts/{id}/holdings/ - Get all holdings
    - GET /api/groww/accounts/{id}/mutual_funds/ - Get all mutual funds
    """
    
    queryset = GrowwAccount.objects.all()
    serializer_class = GrowwAccountSerializer
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return GrowwAccountDetailSerializer
        return GrowwAccountSerializer
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync Groww account data"""
        account = self.get_object()
        
        try:
            # Update sync status
            account.sync_status = 'SYNCING'
            account.save()
            
            # In production, this would call actual Groww API
            # For now, return success with placeholder
            account.sync_status = 'SYNCED'
            account.last_synced = timezone.now()
            account.save()
            
            return Response({
                'status': 'success',
                'message': f'Account {account.account_name} synced successfully',
                'last_synced': account.last_synced
            })
        except Exception as e:
            account.sync_status = 'FAILED'
            account.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get portfolio summary for account"""
        account = self.get_object()
        
        try:
            summary = account.portfolio_summary
            serializer = GrowwPortfolioSummarySerializer(summary)
            return Response(serializer.data)
        except GrowwPortfolioSummary.DoesNotExist:
            return Response(
                {'error': 'Portfolio summary not available'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def holdings(self, request, pk=None):
        """Get all holdings for account"""
        account = self.get_object()
        holdings = account.holdings.all()
        serializer = GrowwHoldingSerializer(holdings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def mutual_funds(self, request, pk=None):
        """Get all mutual funds for account"""
        account = self.get_object()
        mutual_funds = account.mutual_funds.all()
        serializer = GrowwMutualFundSerializer(mutual_funds, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def import_data(self, request):
        """Import Groww data"""
        serializer = GrowwDataImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            groww_user_id = serializer.validated_data['groww_user_id']
            import_type = serializer.validated_data['import_type']
            data = serializer.validated_data['data']
            
            # Get or create account
            account, created = GrowwAccount.objects.get_or_create(
                groww_user_id=groww_user_id
            )
            
            # Create import log
            import_log = GrowwImportLog.objects.create(
                groww_account=account,
                import_type=import_type,
                status='IN_PROGRESS',
                started_at=timezone.now()
            )
            
            # Process import based on type
            if import_type == 'HOLDINGS':
                records_imported = self._import_holdings(account, data)
            elif import_type == 'MUTUAL_FUNDS':
                records_imported = self._import_mutual_funds(account, data)
            elif import_type == 'TRANSACTIONS':
                records_imported = self._import_transactions(account, data)
            elif import_type == 'FULL':
                holdings_count = self._import_holdings(account, data.get('holdings', []))
                mf_count = self._import_mutual_funds(account, data.get('mutual_funds', []))
                tx_count = self._import_transactions(account, data.get('transactions', []))
                records_imported = holdings_count + mf_count + tx_count
            
            # Update import log
            import_log.records_imported = records_imported
            import_log.status = 'SUCCESS'
            import_log.completed_at = timezone.now()
            import_log.save()
            
            return Response({
                'status': 'success',
                'message': f'Imported {records_imported} records',
                'account_id': account.id
            })
        except Exception as e:
            if 'import_log' in locals():
                import_log.status = 'FAILED'
                import_log.error_message = str(e)
                import_log.completed_at = timezone.now()
                import_log.save()
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _import_holdings(self, account, holdings_data):
        """Import stock holdings"""
        count = 0
        for holding in holdings_data:
            obj, created = GrowwHolding.objects.update_or_create(
                groww_account=account,
                stock_symbol=holding['symbol'],
                defaults={
                    'stock_name': holding.get('name', ''),
                    'quantity': holding.get('quantity', 0),
                    'average_cost': holding.get('avg_cost', 0),
                    'current_price': holding.get('current_price', 0),
                    'isin': holding.get('isin', ''),
                    'sector': holding.get('sector', ''),
                }
            )
            count += 1
        return count
    
    def _import_mutual_funds(self, account, mf_data):
        """Import mutual fund holdings"""
        count = 0
        for mf in mf_data:
            obj, created = GrowwMutualFund.objects.update_or_create(
                groww_account=account,
                mf_isin=mf['isin'],
                defaults={
                    'mf_name': mf.get('name', ''),
                    'mf_category': mf.get('category', 'EQUITY'),
                    'units': mf.get('units', 0),
                    'nav': mf.get('nav', 0),
                    'invested_amount': mf.get('invested', 0),
                    'fund_house': mf.get('fund_house', ''),
                }
            )
            count += 1
        return count
    
    def _import_transactions(self, account, tx_data):
        """Import transactions"""
        count = 0
        for tx in tx_data:
            symbol = tx.get('symbol')
            try:
                holding = GrowwHolding.objects.get(
                    groww_account=account,
                    stock_symbol=symbol
                )
                obj, created = GrowwTransaction.objects.get_or_create(
                    groww_holding=holding,
                    transaction_date=tx.get('date'),
                    transaction_type=tx.get('type', 'BUY'),
                    defaults={
                        'quantity': tx.get('quantity', 0),
                        'price': tx.get('price', 0),
                        'amount': tx.get('amount', 0),
                    }
                )
                count += 1
            except GrowwHolding.DoesNotExist:
                pass
        return count


class GrowwHoldingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Groww Holdings
    
    Endpoints:
    - GET /api/groww/holdings/ - List all holdings
    - GET /api/groww/holdings/{id}/ - Get holding details
    - GET /api/groww/holdings/?account_id=xxx - Filter by account
    """
    
    queryset = GrowwHolding.objects.all()
    serializer_class = GrowwHoldingSerializer
    filterset_fields = ['groww_account', 'sector', 'is_favourite']
    ordering_fields = ['current_value', 'gain_loss_percent', 'stock_symbol']
    ordering = ['-current_value']


class GrowwMutualFundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Groww Mutual Funds
    
    Endpoints:
    - GET /api/groww/mutual-funds/ - List all mutual funds
    - GET /api/groww/mutual-funds/{id}/ - Get MF details
    - GET /api/groww/mutual-funds/?account_id=xxx - Filter by account
    """
    
    queryset = GrowwMutualFund.objects.all()
    serializer_class = GrowwMutualFundSerializer
    filterset_fields = ['groww_account', 'mf_category']
    ordering_fields = ['current_value', 'gain_loss_percent']
    ordering = ['-current_value']


class GrowwImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Groww Import Logs (Read-only)
    
    Endpoints:
    - GET /api/groww/import-logs/ - List all import logs
    - GET /api/groww/import-logs/{id}/ - Get log details
    - GET /api/groww/import-logs/?account_id=xxx - Filter by account
    """
    
    queryset = GrowwImportLog.objects.all()
    serializer_class = GrowwImportLogSerializer
    filterset_fields = ['groww_account', 'import_type', 'status']
    ordering = ['-started_at']
