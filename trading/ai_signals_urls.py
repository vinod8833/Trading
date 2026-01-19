"""
URL Configuration for AI Data Integration & Signal Generation
"""

from django.urls import path
from trading.ai_signals_views import (
    GenerateTradingSignalView,
    FetchMarketDataView,
    CalculateIndicatorsView,
    PredictPriceMovementView,
    MarketStatusView,
    RefreshAllSignalsView,
    DataQualityCheckView
)

app_name = "ai_signals"

urlpatterns = [
    path("generate-signal/", GenerateTradingSignalView.as_view(), name="generate-signal"),
    path("refresh-signals/", RefreshAllSignalsView.as_view(), name="refresh-signals"),

    path("market-data/", FetchMarketDataView.as_view(), name="market-data"),
    path("market-status/", MarketStatusView.as_view(), name="market-status"),
    
    path("calculate-indicators/", CalculateIndicatorsView.as_view(), name="calculate-indicators"),
    path("predict-movement/", PredictPriceMovementView.as_view(), name="predict-movement"),
    
    path("data-quality/", DataQualityCheckView.as_view(), name="data-quality"),
]
