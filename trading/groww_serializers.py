"""
Serializers for Groww Integration
"""

from rest_framework import serializers
from .models import (
    GrowwAccount, GrowwHolding, GrowwMutualFund,
    GrowwPortfolioSummary, GrowwTransaction, GrowwImportLog
)


class GrowwTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Groww Transactions"""
    
    class Meta:
        model = GrowwTransaction
        fields = [
            'id', 'transaction_type', 'quantity', 'price', 'amount',
            'transaction_date', 'transaction_time', 'brokerage', 'tax', 'notes'
        ]


class GrowwHoldingSerializer(serializers.ModelSerializer):
    """Serializer for Groww Holdings"""
    
    transactions = GrowwTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = GrowwHolding
        fields = [
            'id', 'stock_symbol', 'stock_name', 'isin', 'quantity',
            'average_cost', 'current_price', 'total_invested', 'current_value',
            'gain_loss', 'gain_loss_percent', 'sector', 'industry',
            'purchase_date', 'is_favourite', 'notes', 'transactions'
        ]


class GrowwMutualFundSerializer(serializers.ModelSerializer):
    """Serializer for Groww Mutual Funds"""
    
    class Meta:
        model = GrowwMutualFund
        fields = [
            'id', 'mf_isin', 'mf_name', 'mf_category', 'units', 'nav',
            'invested_amount', 'current_value', 'gain_loss', 'gain_loss_percent',
            'fund_house', 'expense_ratio'
        ]


class GrowwPortfolioSummarySerializer(serializers.ModelSerializer):
    """Serializer for Groww Portfolio Summary"""
    
    class Meta:
        model = GrowwPortfolioSummary
        fields = [
            'total_invested', 'current_portfolio_value', 'total_gain_loss',
            'total_gain_loss_percent', 'equity_value', 'mutual_fund_value',
            'cash_balance', 'total_holdings', 'total_mutual_funds',
            'equity_allocation_percent', 'debt_allocation_percent',
            'others_allocation_percent', 'portfolio_beta', 'volatility',
            'sharpe_ratio', 'updated_at'
        ]
        read_only_fields = fields


class GrowwAccountDetailSerializer(serializers.ModelSerializer):
    """Detailed Groww Account Serializer with holdings"""
    
    holdings = GrowwHoldingSerializer(many=True, read_only=True)
    mutual_funds = GrowwMutualFundSerializer(many=True, read_only=True)
    portfolio_summary = GrowwPortfolioSummarySerializer(read_only=True)
    
    class Meta:
        model = GrowwAccount
        fields = [
            'id', 'groww_user_id', 'account_name', 'account_type', 'email',
            'phone', 'pan', 'is_verified', 'verification_date',
            'sync_status', 'last_synced', 'holdings', 'mutual_funds',
            'portfolio_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'holdings', 'mutual_funds', 'portfolio_summary']


class GrowwAccountSerializer(serializers.ModelSerializer):
    """Basic Groww Account Serializer"""
    
    class Meta:
        model = GrowwAccount
        fields = [
            'id', 'groww_user_id', 'account_name', 'account_type', 'email',
            'phone', 'is_verified', 'sync_status', 'last_synced', 'created_at'
        ]
        read_only_fields = ['created_at']


class GrowwImportLogSerializer(serializers.ModelSerializer):
    """Serializer for Groww Import Logs"""
    
    groww_account = GrowwAccountSerializer(read_only=True)
    
    class Meta:
        model = GrowwImportLog
        fields = [
            'id', 'groww_account', 'import_type', 'status',
            'records_imported', 'records_updated', 'records_failed',
            'error_message', 'started_at', 'completed_at'
        ]
        read_only_fields = fields


class GrowwPortfolioComparisonSerializer(serializers.Serializer):
    """Serializer for comparing Groww portfolio with platform portfolio"""
    
    groww_account = GrowwAccountSerializer()
    groww_summary = GrowwPortfolioSummarySerializer()
    
    # Comparison metrics
    total_stocks = serializers.IntegerField()
    total_mutual_funds = serializers.IntegerField()
    total_holdings = serializers.IntegerField()
    
    # Top holdings
    top_holdings = GrowwHoldingSerializer(many=True)
    top_mutual_funds = GrowwMutualFundSerializer(many=True)
    
    # Sector allocation
    sector_allocation = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Performance metrics
    ytd_return = serializers.FloatField()
    three_month_return = serializers.FloatField()
    one_year_return = serializers.FloatField()


class GrowwDataImportSerializer(serializers.Serializer):
    """Serializer for importing Groww data"""
    
    IMPORT_TYPE_CHOICES = [
        ('HOLDINGS', 'Holdings'),
        ('MUTUAL_FUNDS', 'Mutual Funds'),
        ('TRANSACTIONS', 'Transactions'),
        ('FULL', 'Full Sync'),
    ]
    
    groww_user_id = serializers.CharField(max_length=255)
    import_type = serializers.ChoiceField(choices=IMPORT_TYPE_CHOICES)
    data = serializers.JSONField()  # Raw import data
    
    def validate_import_type(self, value):
        """Validate import type"""
        valid_types = ['HOLDINGS', 'MUTUAL_FUNDS', 'TRANSACTIONS', 'FULL']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid import type. Must be one of: {', '.join(valid_types)}"
            )
        return value
