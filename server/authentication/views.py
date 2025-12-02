from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User
from .serializers import LoginSerializer, UserSerializer, ChangePasswordSerializer
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            # Debug logging
            print(f"=== Login Request Debug ===")
            print(f"Request data: {request.data}")
            print(f"Content-Type: {request.content_type}")
            
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                # Add custom claims
                refresh['email'] = user.email
                refresh['role'] = user.role
                
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        'user': UserSerializer(user).data,
                        'tokens': {
                            'access': str(refresh.access_token),
                            'refresh': str(refresh)
                        }
                    }
                }, status=status.HTTP_200_OK)
            
            # Handle validation errors
            error_message = 'Login failed'
            
            # Debug logging for errors
            print(f"Serializer errors: {serializer.errors}")
            
            # Check if there's a non_field_errors (general validation error)
            if 'non_field_errors' in serializer.errors:
                error_message = serializer.errors['non_field_errors'][0]
            
            return Response({
                'success': False,
                'message': error_message,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred during login',
                'errors': {'general': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except TokenError:
            return Response({
                'success': False,
                'message': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred during logout'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while fetching profile'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            
            if serializer.is_valid():
                user = request.user
                
                # Check old password
                if not user.check_password(serializer.validated_data['old_password']):
                    return Response({
                        'success': False,
                        'message': 'Current password is incorrect'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Set new password
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Password changed successfully'
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Password change failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while changing password'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(APIView):
    """
    Get list of users filtered by role (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # Only admin can access this endpoint
            if request.user.role != 'admin':
                return Response({
                    'success': False,
                    'message': 'Permission denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get role from query params
            role = request.query_params.get('role', None)
            
            # Filter users by role if provided
            if role:
                users = User.objects.filter(role=role).order_by('last_name', 'first_name')
            else:
                users = User.objects.all().order_by('last_name', 'first_name')
            
            # RBAC: Department head restrictions for faculty list
            if role == 'faculty' and request.user.admin_subrole:
                if request.user.admin_subrole == 'dept_head_cs':
                    # CS Department Head: only CS faculty
                    users = users.filter(department='CS')
                elif request.user.admin_subrole == 'dept_head_it':
                    # IT Department Head: IT and ICT faculty
                    users = users.filter(department__in=['IT', 'ICT'])
                # dean has no restrictions (sees all)
            
            # Serialize the users
            serializer = UserSerializer(users, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"User list fetch error: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred while fetching users'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

