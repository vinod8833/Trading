"""
User API URLs
"""

from django.urls import path
from trading.user_views import UserViewSet

urlpatterns = [
    path('profile/', UserViewSet.as_view({'get': 'profile', 'put': 'profile'}), name='user-profile'),
    path('settings/', UserViewSet.as_view({'get': 'settings', 'put': 'settings'}), name='user-settings'),
    path('change-password/', UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
]
