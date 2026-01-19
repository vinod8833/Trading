
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that includes user info in response"""
    
    def get_token(self, user):
        token = super().get_token(user)
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom view using the custom serializer"""
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
