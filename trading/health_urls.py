"""
Health Check & Status URLs
"""

from django.http import JsonResponse
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status as http_status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Comprehensive health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get system health status"""
        from .market_data_service import MarketDataService, MarketCalendar
        from django.db import connection
        from django.contrib.auth.models import User
        
        health_data = {
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system': 'KVK_8833_PROFIT_AI_TRADING',
            'version': '2.0',
        }
        
        try:
            # Check database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['database'] = 'connected'
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            health_data['database'] = 'disconnected'
            health_data['status'] = 'degraded'
        
        try:
            # Check market status
            market_status = MarketDataService.get_market_status()
            health_data['market'] = market_status
        except Exception as e:
            logger.warning(f"Could not fetch market status: {e}")
            health_data['market'] = {
                'is_open': False,
                'status': 'UNKNOWN',
                'error': str(e)
            }
        
        try:
            # Count users
            user_count = User.objects.count()
            health_data['users'] = user_count
        except Exception as e:
            logger.warning(f"Could not count users: {e}")
            health_data['users'] = 0
        
        # API endpoints status
        health_data['api_endpoints'] = {
            'authentication': '/api/auth/token/',
            'stocks': '/api/stocks/',
            'recommendations': '/api/recommendations/generate/',
            'intraday': '/api/intraday-signals/',
            'paper_trading': '/api/paper-trading/',
            'scanner': '/api/stock-scanner/',
            'market': '/api/market-summary/',
            'profile': '/api/users/profile/',
            'ai_engine': '/api/ai/generate-signal/',
        }
        
        return Response(health_data, status=http_status.HTTP_200_OK)


def health_check_simple(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'system': 'KVK_8833_PROFIT',
        'message': 'Trading system is operational',
        'timestamp': datetime.now().isoformat(),
    })


urlpatterns = [
    path('', health_check_simple, name='health_check_simple'),
    path('detailed/', HealthCheckView.as_view(), name='health_check_detailed'),
]
