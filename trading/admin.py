from django.contrib import admin
from .models import (
    Stock, StockAnalysis, TradeRecommendation, TradeOrder,
    Portfolio, RiskAssessment, AlternativeInvestment,
    PaperTrade, SmartAlert, MarketSummary, PortfolioHealth,
    TradingMistake, AIExplanation, InvestmentPlan,
    GrowwAccount, GrowwHolding, GrowwMutualFund,
    GrowwPortfolioSummary, GrowwTransaction, GrowwImportLog,
    StockPriceSnapshot, MarketIndex, SectorPerformance,
    TradeSignal, SignalHistory, DataSource
)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'market_cap_category', 'current_price', 'updated_at']
    list_filter = ['market_cap_category', 'sector']
    search_fields = ['symbol', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StockAnalysis)
class StockAnalysisAdmin(admin.ModelAdmin):
    list_display = ['stock', 'trend', 'rsi', 'trend_probability', 'analyzed_at']
    list_filter = ['trend', 'volume_trend']
    search_fields = ['stock__symbol']
    readonly_fields = ['analyzed_at']


@admin.register(TradeRecommendation)
class TradeRecommendationAdmin(admin.ModelAdmin):
    list_display = ['stock', 'trading_style', 'signal', 'entry_price', 'confidence_level']
    list_filter = ['signal', 'trading_style', 'confidence_level']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at']


@admin.register(TradeOrder)
class TradeOrderAdmin(admin.ModelAdmin):
    list_display = ['stock', 'quantity', 'entry_price', 'status', 'profit_loss']
    list_filter = ['status', 'created_at']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_capital', 'available_capital', 'total_profit_loss']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['recommendation', 'risk_level', 'risk_percentage', 'created_at']
    list_filter = ['risk_level']
    readonly_fields = ['created_at']


@admin.register(AlternativeInvestment)
class AlternativeInvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'investment_type', 'expected_return', 'risk_level']
    list_filter = ['investment_type', 'risk_level']
    search_fields = ['name']


@admin.register(PaperTrade)
class PaperTradeAdmin(admin.ModelAdmin):
    list_display = ['stock', 'quantity', 'entry_price', 'status', 'profit_loss_percent']
    list_filter = ['status', 'created_at']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SmartAlert)
class SmartAlertAdmin(admin.ModelAdmin):
    list_display = ['stock', 'alert_type', 'status', 'target_value', 'triggered_at']
    list_filter = ['alert_type', 'status']
    search_fields = ['stock__symbol']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MarketSummary)
class MarketSummaryAdmin(admin.ModelAdmin):
    list_display = ['market_date', 'market_sentiment', 'gainers_count', 'losers_count']
    list_filter = ['market_date', 'market_sentiment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PortfolioHealth)
class PortfolioHealthAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'health_status', 'health_score', 'profit_loss_percent']
    list_filter = ['health_status']
    search_fields = ['portfolio__name']
    readonly_fields = ['analyzed_at']


@admin.register(TradingMistake)
class TradingMistakeAdmin(admin.ModelAdmin):
    list_display = ['trade_order', 'mistake_category', 'severity', 'impact']
    list_filter = ['mistake_category', 'severity']
    search_fields = ['trade_order__stock__symbol']
    readonly_fields = ['detected_at']


@admin.register(AIExplanation)
class AIExplanationAdmin(admin.ModelAdmin):
    list_display = ['explanation_type', 'confidence_score', 'created_at']
    list_filter = ['explanation_type']
    readonly_fields = ['created_at']


@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'goal', 'target_amount', 'expected_returns']
    list_filter = ['goal', 'time_horizon']
    search_fields = ['portfolio__name']
    readonly_fields = ['created_at', 'updated_at']




@admin.register(GrowwAccount)
class GrowwAccountAdmin(admin.ModelAdmin):
    list_display = ['account_name', 'email', 'account_type', 'is_verified', 'sync_status', 'last_synced']
    list_filter = ['account_type', 'is_verified', 'sync_status']
    search_fields = ['account_name', 'email', 'groww_user_id']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Account Information', {
            'fields': ('groww_user_id', 'account_name', 'account_type', 'email', 'phone', 'pan')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date')
        }),
        ('Sync Status', {
            'fields': ('sync_status', 'last_synced')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrowwHolding)
class GrowwHoldingAdmin(admin.ModelAdmin):
    list_display = ['stock_symbol', 'stock_name', 'quantity', 'average_cost', 'current_value', 'gain_loss_percent']
    list_filter = ['sector', 'is_favourite']
    search_fields = ['stock_symbol', 'stock_name', 'groww_account__account_name']
    readonly_fields = ['created_at', 'updated_at', 'total_invested', 'current_value', 'gain_loss', 'gain_loss_percent']
    fieldsets = (
        ('Account & Stock', {
            'fields': ('groww_account', 'stock_symbol', 'stock_name', 'isin')
        }),
        ('Holding Details', {
            'fields': ('quantity', 'average_cost', 'current_price', 'purchase_date')
        }),
        ('Valuation', {
            'fields': ('total_invested', 'current_value', 'gain_loss', 'gain_loss_percent'),
            'classes': ('collapse',)
        }),
        ('Classification', {
            'fields': ('sector', 'industry', 'is_favourite')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrowwMutualFund)
class GrowwMutualFundAdmin(admin.ModelAdmin):
    list_display = ['mf_name', 'mf_category', 'units', 'nav', 'current_value', 'gain_loss_percent']
    list_filter = ['mf_category', 'fund_house']
    search_fields = ['mf_name', 'mf_isin', 'groww_account__account_name']
    readonly_fields = ['created_at', 'updated_at', 'current_value', 'gain_loss', 'gain_loss_percent']
    fieldsets = (
        ('Account & Fund', {
            'fields': ('groww_account', 'mf_isin', 'mf_name', 'fund_house')
        }),
        ('Fund Details', {
            'fields': ('mf_category', 'expense_ratio', 'nav')
        }),
        ('Holdings', {
            'fields': ('units', 'invested_amount')
        }),
        ('Valuation', {
            'fields': ('current_value', 'gain_loss', 'gain_loss_percent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrowwPortfolioSummary)
class GrowwPortfolioSummaryAdmin(admin.ModelAdmin):
    list_display = ['groww_account', 'current_portfolio_value', 'total_gain_loss', 'total_gain_loss_percent']
    readonly_fields = [
        'updated_at', 'total_invested', 'current_portfolio_value',
        'total_gain_loss', 'total_gain_loss_percent', 'portfolio_beta', 'volatility', 'sharpe_ratio'
    ]
    fieldsets = (
        ('Account', {
            'fields': ('groww_account',)
        }),
        ('Portfolio Values', {
            'fields': ('total_invested', 'current_portfolio_value', 'total_gain_loss', 'total_gain_loss_percent')
        }),
        ('Breakdown', {
            'fields': ('equity_value', 'mutual_fund_value', 'cash_balance', 'total_holdings', 'total_mutual_funds')
        }),
        ('Allocation', {
            'fields': ('equity_allocation_percent', 'debt_allocation_percent', 'others_allocation_percent')
        }),
        ('Risk Metrics', {
            'fields': ('portfolio_beta', 'volatility', 'sharpe_ratio'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrowwTransaction)
class GrowwTransactionAdmin(admin.ModelAdmin):
    list_display = ['groww_holding', 'transaction_type', 'quantity', 'price', 'amount', 'transaction_date']
    list_filter = ['transaction_type', 'transaction_date']
    search_fields = ['groww_holding__stock_symbol', 'groww_holding__groww_account__account_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'transaction_date'
    fieldsets = (
        ('Holding', {
            'fields': ('groww_holding',)
        }),
        ('Transaction Details', {
            'fields': ('transaction_type', 'quantity', 'price', 'amount', 'transaction_date', 'transaction_time')
        }),
        ('Costs', {
            'fields': ('brokerage', 'tax')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GrowwImportLog)
class GrowwImportLogAdmin(admin.ModelAdmin):
    list_display = ['groww_account', 'import_type', 'status', 'records_imported', 'records_updated', 'records_failed', 'started_at']
    list_filter = ['import_type', 'status', 'started_at']
    search_fields = ['groww_account__account_name']
    readonly_fields = ['started_at', 'completed_at']
    date_hierarchy = 'started_at'
    fieldsets = (
        ('Import Information', {
            'fields': ('groww_account', 'import_type', 'status')
        }),
        ('Results', {
            'fields': ('records_imported', 'records_updated', 'records_failed')
        }),
        ('Errors', {
            'fields': ('error_message',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at')
        }),
    )


@admin.register(StockPriceSnapshot)
class StockPriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'current_price', 'previous_close', 'volume', 'data_freshness', 'market_status', 'timestamp']
    list_filter = ['data_freshness', 'market_status', 'data_source', 'timestamp']
    search_fields = ['symbol']
    readonly_fields = ['timestamp', 'updated_at']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Price Information', {
            'fields': ('symbol', 'current_price', 'previous_close', 'open_price', 'high_price', 'low_price')
        }),
        ('Volume & Value', {
            'fields': ('volume', 'traded_value')
        }),
        ('Metrics', {
            'fields': ('market_cap', 'pe_ratio')
        }),
        ('Data Source', {
            'fields': ('data_source', 'data_freshness', 'market_status')
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketIndex)
class MarketIndexAdmin(admin.ModelAdmin):
    list_display = ['index_name', 'current_value', 'change_points', 'change_percent', 'timestamp']
    list_filter = ['index_name', 'timestamp']
    readonly_fields = ['timestamp', 'updated_at']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Index Information', {
            'fields': ('index_name', 'symbol')
        }),
        ('Values', {
            'fields': ('current_value', 'previous_close', 'change_points', 'change_percent')
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SectorPerformance)
class SectorPerformanceAdmin(admin.ModelAdmin):
    list_display = ['sector', 'current_value', 'change_percent', 'timestamp']
    list_filter = ['sector', 'timestamp']
    readonly_fields = ['timestamp', 'updated_at']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Sector Information', {
            'fields': ('sector', 'index_symbol')
        }),
        ('Performance', {
            'fields': ('current_value', 'change_percent')
        }),
        ('Top Movers', {
            'fields': ('top_gainers', 'top_losers')
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TradeSignal)
class TradeSignalAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'signal', 'confidence', 'entry_price', 'target_price', 'stop_loss', 'data_quality', 'generated_at']
    list_filter = ['signal', 'data_quality', 'trend', 'momentum', 'generated_at']
    search_fields = ['symbol']
    readonly_fields = ['generated_at', 'updated_at']
    date_hierarchy = 'generated_at'
    fieldsets = (
        ('Signal Information', {
            'fields': ('symbol', 'signal', 'confidence', 'confidence_min', 'confidence_max')
        }),
        ('Trading Levels', {
            'fields': ('entry_price', 'target_price', 'stop_loss', 'risk_reward_ratio')
        }),
        ('Technical Analysis', {
            'fields': ('technical_patterns', 'volume_signal', 'trend', 'momentum', 'volatility')
        }),
        ('Probabilities', {
            'fields': ('uptrend_probability', 'breakout_probability', 'support_hold_probability')
        }),
        ('Risk Warnings', {
            'fields': ('warning_flags',)
        }),
        ('Quality & Reason', {
            'fields': ('data_quality', 'confidence_reason')
        }),
        ('Disclaimer', {
            'fields': ('disclaimer',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('generated_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SignalHistory)
class SignalHistoryAdmin(admin.ModelAdmin):
    list_display = ['signal', 'entry_price', 'exit_price', 'exit_reason', 'profit_loss_percent', 'signal_accuracy', 'created_at']
    list_filter = ['exit_reason', 'signal_accuracy', 'created_at']
    search_fields = ['signal__symbol']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Signal Reference', {
            'fields': ('signal',)
        }),
        ('Entry', {
            'fields': ('entry_price', 'entry_time')
        }),
        ('Exit', {
            'fields': ('exit_price', 'exit_time', 'exit_reason')
        }),
        ('Performance', {
            'fields': ('profit_loss_rupees', 'profit_loss_percent', 'signal_accuracy')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_free', 'requires_api_key', 'is_available', 'availability_percent', 'last_checked']
    list_filter = ['is_free', 'is_available', 'provides_price', 'provides_fundamentals', 'update_frequency']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Source Information', {
            'fields': ('name', 'url', 'description')
        }),
        ('Data Provided', {
            'fields': ('provides_price', 'provides_fundamentals', 'provides_technical', 'provides_news', 'provides_corporate_actions')
        }),
        ('Access', {
            'fields': ('is_free', 'requires_api_key')
        }),
        ('Update Frequency', {
            'fields': ('update_frequency',)
        }),
        ('Health', {
            'fields': ('is_available', 'availability_percent', 'last_checked')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
