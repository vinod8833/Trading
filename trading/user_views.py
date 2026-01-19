"""
User Profile and Settings Views
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class UserProfileView(APIView):
    """API View for user profile"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get user profile"""
        if request.user and request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        else:
            # Return mock data for unauthenticated users
            return Response({
                'id': 1,
                'username': 'demo_user',
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User',
            })
    
    def put(self, request):
        """Update user profile"""
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'User must be authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSettingsView(APIView):
    """API View for user settings"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get user settings"""
        return Response({
            'trading_style': 'conservative',
            'risk_percentage': 5,
            'enable_notifications': True,
            'enable_email_alerts': False,
            'enable_sms_alerts': False,
            'theme': 'light',
        })
    
    def put(self, request):
        """Update user settings"""
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'User must be authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        default_settings = {
            'trading_style': request.data.get('trading_style', 'conservative'),
            'risk_percentage': request.data.get('risk_percentage', 5),
            'enable_notifications': request.data.get('enable_notifications', True),
            'enable_email_alerts': request.data.get('enable_email_alerts', False),
            'enable_sms_alerts': request.data.get('enable_sms_alerts', False),
            'theme': request.data.get('theme', 'light'),
        }
        return Response(default_settings)


class UserChangePasswordView(APIView):
    """API View for changing password"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Change user password"""
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'User must be authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': 'Password changed successfully'})


# Keep UserViewSet for backward compatibility with router registration
from rest_framework import viewsets

class UserViewSet(viewsets.ViewSet):
    """Dummy ViewSet for router registration"""
    permission_classes = [AllowAny]
    
    def list(self, request):
        return Response({'message': 'Use profile/ or settings/ endpoints'})


