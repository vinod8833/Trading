
from django.urls import path
from .ai_trading_api import (
    ComprehensiveTradeAnalysisView,
    DataQualityReportView,
    MarketStatusView,
    SignalExplanationView,
    SignalValidationView
)

app_name = 'ai_trading'

urlpatterns = [
    path(
        'analyze-trade/',
        ComprehensiveTradeAnalysisView.as_view(),
        name='analyze-trade'
    ),
    
    path(
        'assess-data-quality/',
        DataQualityReportView.as_view(),
        name='assess-data-quality'
    ),
    
    path(
        'market-status/',
        MarketStatusView.as_view(),
        name='market-status'
    ),
    
    path(
        'explain-signal/',
        SignalExplanationView.as_view(),
        name='explain-signal'
    ),
    
    path(
        'validate-signal/',
        SignalValidationView.as_view(),
        name='validate-signal'
    ),
]
