"""
Serializers for Market Data and AI Signal Models
"""

from rest_framework import serializers
from .models import (
    StockPriceSnapshot, MarketIndex, SectorPerformance,
    TradeSignal, SignalHistory, DataSource
)


class StockPriceSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for stock price snapshots"""
    
    class Meta:
        model = StockPriceSnapshot
        fields = [
            'id', 'symbol', 'current_price', 'previous_close', 'open_price',
            'high_price', 'low_price', 'volume', 'traded_value', 'market_cap',
            'pe_ratio', 'data_source', 'data_freshness', 'market_status', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class MarketIndexSerializer(serializers.ModelSerializer):
    """Serializer for market indices"""
    
    class Meta:
        model = MarketIndex
        fields = [
            'id', 'index_name', 'symbol', 'current_value', 'previous_close',
            'change_points', 'change_percent', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class SectorPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for sector performance"""
    
    class Meta:
        model = SectorPerformance
        fields = [
            'id', 'sector', 'index_symbol', 'current_value', 'change_percent',
            'top_gainers', 'top_losers', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class TradeSignalSerializer(serializers.ModelSerializer):
    """Serializer for trade signals with full details"""
    
    class Meta:
        model = TradeSignal
        fields = [
            'id', 'symbol', 'signal', 'confidence', 'confidence_min', 'confidence_max',
            'entry_price', 'target_price', 'stop_loss', 'risk_reward_ratio',
            'technical_patterns', 'volume_signal', 'trend', 'momentum', 'volatility',
            'uptrend_probability', 'breakout_probability', 'support_hold_probability',
            'warning_flags', 'data_quality', 'confidence_reason', 'disclaimer',
            'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class TradeSignalListSerializer(serializers.ModelSerializer):
    """Simplified serializer for signal lists"""
    
    class Meta:
        model = TradeSignal
        fields = [
            'id', 'symbol', 'signal', 'confidence', 'entry_price', 'target_price',
            'stop_loss', 'risk_reward_ratio', 'trend', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class SignalHistorySerializer(serializers.ModelSerializer):
    """Serializer for signal performance tracking"""
    
    signal_symbol = serializers.CharField(source='signal.symbol', read_only=True)
    
    class Meta:
        model = SignalHistory
        fields = [
            'id', 'signal', 'signal_symbol', 'entry_price', 'entry_time',
            'exit_price', 'exit_time', 'exit_reason', 'profit_loss_rupees',
            'profit_loss_percent', 'signal_accuracy', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for data sources"""
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'url', 'description', 'provides_price', 'provides_fundamentals',
            'provides_technical', 'provides_news', 'provides_corporate_actions',
            'is_free', 'requires_api_key', 'update_frequency', 'last_checked',
            'is_available', 'availability_percent'
        ]
        read_only_fields = ['id']
