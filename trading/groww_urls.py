"""
URL Configuration for Groww Integration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .groww_viewsets import (
    GrowwAccountViewSet, GrowwHoldingViewSet,
    GrowwMutualFundViewSet, GrowwImportLogViewSet
)

router = DefaultRouter()
router.register(r'accounts', GrowwAccountViewSet, basename='groww-account')
router.register(r'holdings', GrowwHoldingViewSet, basename='groww-holding')
router.register(r'mutual-funds', GrowwMutualFundViewSet, basename='groww-mutual-fund')
router.register(r'import-logs', GrowwImportLogViewSet, basename='groww-import-log')

urlpatterns = [
    path('', include(router.urls)),
]
