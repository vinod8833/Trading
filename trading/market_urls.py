"""
URL Configuration for Market Data and Trading Signals API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .market_viewsets import (
    StockPriceSnapshotViewSet, MarketIndexViewSet, SectorPerformanceViewSet,
    TradeSignalViewSet, SignalHistoryViewSet, DataSourceViewSet
)

router = DefaultRouter()
router.register(r'prices', StockPriceSnapshotViewSet, basename='price')
router.register(r'indices', MarketIndexViewSet, basename='index')
router.register(r'sectors', SectorPerformanceViewSet, basename='sector')
router.register(r'signals', TradeSignalViewSet, basename='signal')
router.register(r'signal-history', SignalHistoryViewSet, basename='signal-history')
router.register(r'data-sources', DataSourceViewSet, basename='data-source')

urlpatterns = [
    path('', include(router.urls)),
]
