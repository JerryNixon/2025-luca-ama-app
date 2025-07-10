from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
import secrets
import string

from .models import User, Event, Question, Vote
from .serializers import (
    UserSerializer, LoginSerializer, EventSerializer, 
    QuestionSerializer, VoteSerializer
)

# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login endpoint - returns JWT token"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })
    return Response({
        'success': False,
        'message': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    """Logout endpoint"""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'success': True, 'message': 'Logged out successfully'})
    except Exception:
        return Response({'success': False, 'message': 'Logout failed'}, 
                       status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def me_view(request):
    """Get current user info"""
    if request.user.is_authenticated:
        return Response({
            'success': True,
            'data': UserSerializer(request.user).data
        })
    return Response({'success': False, 'message': 'Not authenticated'}, 
                   status=status.HTTP_401_UNAUTHORIZED)

# ============================================================================
# EVENT VIEWS
# ============================================================================

class EventListCreateView(generics.ListCreateAPIView):
    """List events and create new events - User-specific access model"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Only return events the user has access to
        return user.get_accessible_events().annotate(
            question_count=Count('questions')
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Generate unique share link and invite link
        share_link = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        invite_link = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        event = serializer.save(
            created_by=self.request.user,
            share_link=share_link,
            invite_link=invite_link,
            is_public=False  # Default to private
        )
        
        # Creator automatically becomes a moderator
        event.moderators.add(self.request.user)
        
        # Note: Additional moderators are handled by the serializer's create method

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete specific event - Dynamic permissions"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return all events, permission checking is done in get_object
        return Event.objects.filter(is_active=True)
    
    def get_object(self):
        """Override to implement dynamic permissions"""
        obj = super().get_object()
        user = self.request.user
        
        # Check if user can access this event
        if not obj.can_user_access(user):
            from django.http import Http404
            raise Http404("Event not found or access denied")
        
        return obj
    
    def update(self, request, *args, **kwargs):
        """Override to check moderation permissions for updates"""
        obj = self.get_object()
        user = request.user
        
        # Only moderators can update events
        if not obj.can_user_moderate(user):
            return Response(
                {'success': False, 'message': 'You do not have permission to modify this event'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Override to check moderation permissions for deletion"""
        obj = self.get_object()
        user = request.user
        
        # Only creator or system admin can delete events
        if not (obj.created_by == user or user.is_system_admin()):
            return Response(
                {'success': False, 'message': 'You do not have permission to delete this event'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
def join_event_view(request, share_link):
    """Join event via share link"""
    try:
        event = get_object_or_404(Event, share_link=share_link)
        user = request.user
        
        # Check if user is already connected to this event
        if event.can_user_access(user):
            return Response({
                'success': True,
                'data': EventSerializer(event, context={'request': request}).data,
                'message': f'You already have access to {event.name}',
                'role': event.get_user_role_in_event(user)
            })
        
        # Add user as participant
        event.participants.add(user)
        
        return Response({
            'success': True,
            'data': EventSerializer(event, context={'request': request}).data,
            'message': f'Successfully joined {event.name}',
            'role': 'participant'
        })
        
    except Event.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid or expired share link'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])  
def join_event_by_invite(request, invite_link):
    """Join event via invite link"""
    try:
        event = get_object_or_404(Event, invite_link=invite_link)
        user = request.user
        
        # Check if user is already connected to this event
        if event.can_user_access(user):
            return Response({
                'success': True,
                'data': EventSerializer(event, context={'request': request}).data,
                'message': f'You already have access to {event.name}',
                'role': event.get_user_role_in_event(user)
            })
        
        # Add user as participant
        event.participants.add(user)
        
        return Response({
            'success': True,
            'data': EventSerializer(event, context={'request': request}).data,
            'message': f'Successfully joined {event.name}',
            'role': 'participant'
        })
        
    except Event.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Invalid or expired invite link'
        }, status=status.HTTP_404_NOT_FOUND)

# ============================================================================
# QUESTION VIEWS  
# ============================================================================

class QuestionListCreateView(generics.ListCreateAPIView):
    """List questions for an event and create new questions"""
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        
        # Check if user has access to this event using new permission system
        user = self.request.user
        if not event.can_user_access(user):
            return Question.objects.none()
        
        queryset = event.questions.all()
        
        # Apply filters
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(text__icontains=keyword)
        
        is_answered = self.request.query_params.get('isAnswered')
        if is_answered is not None:
            queryset = queryset.filter(is_answered=is_answered.lower() == 'true')
        
        is_starred = self.request.query_params.get('isStarred')
        if is_starred is not None:
            queryset = queryset.filter(is_starred=is_starred.lower() == 'true')
        
        # Sort by upvotes and date
        sort_by = self.request.query_params.get('sortBy', 'votes')
        if sort_by == 'votes':
            queryset = queryset.annotate(vote_count=Count('vote_records')).order_by('-vote_count', '-created_at')
        elif sort_by == 'date':
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def perform_create(self, serializer):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        serializer.save(
            author=self.request.user,
            event=event
        )

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete specific question"""
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Question.objects.all()
    
    def update(self, request, *args, **kwargs):
        question = self.get_object()
        user = request.user
        
        # Check permissions using new permission system
        if (question.author != user and 
            not question.event.can_user_moderate(user)):
            return Response({'success': False, 'message': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Special handling for staging to enforce "only one question on stage at a time"
        if 'is_staged' in request.data:
            # Redirect staging operations to use the dedicated staging endpoint
            if request.data.get('is_staged') and not question.is_staged:
                # If trying to stage a question, ensure only one is staged at a time
                Question.objects.filter(event=question.event).update(is_staged=False)
                question.is_staged = True
                question.save()
            elif not request.data.get('is_staged') and question.is_staged:
                # If unstaging, just unstage this question
                question.is_staged = False
                question.save()
            
            # Remove is_staged from request data to prevent double processing
            request_data = request.data.copy()
            del request_data['is_staged']
            request._full_data = request_data
        
        return super().update(request, *args, **kwargs)

# ============================================================================
# VOTING VIEWS
# ============================================================================

@api_view(['POST'])
def upvote_question_view(request, question_id):
    """Upvote or remove upvote from question"""
    question = get_object_or_404(Question, id=question_id)
    user = request.user
    
    # Check if user has access to this event using new permission system
    if not question.event.can_user_access(user):
        return Response({'success': False, 'message': 'Permission denied'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Toggle vote
    vote, created = Vote.objects.get_or_create(
        question=question,
        user=user
    )
    
    if not created:
        # Remove existing vote
        vote.delete()
        action = 'removed'
    else:
        action = 'added'
    
    # Update question upvote count
    question.upvotes = question.vote_records.count()
    question.save()
    
    return Response({
        'success': True,
        'data': {
            'upvotes': question.upvotes,
            'hasUserUpvoted': action == 'added'
        },
        'message': f'Vote {action}'
    })

# ============================================================================
# MODERATOR ACTIONS
# ============================================================================

@api_view(['POST'])
def star_question_view(request, question_id):
    """Star/unstar question (moderator only)"""
    question = get_object_or_404(Question, id=question_id)
    user = request.user
    
    # Check moderator permissions using new permission system
    if not question.event.can_user_moderate(user):
        return Response({'success': False, 'message': 'Moderator access required'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    question.is_starred = not question.is_starred
    question.save()
    
    return Response({
        'success': True,
        'data': {'isStarred': question.is_starred},
        'message': f'Question {"starred" if question.is_starred else "unstarred"}'
    })

@api_view(['POST'])
def stage_question_view(request, question_id):
    """Stage/unstage question (moderator only)"""
    question = get_object_or_404(Question, id=question_id)
    user = request.user
    
    # Check moderator permissions using new permission system
    if not question.event.can_user_moderate(user):
        return Response({'success': False, 'message': 'Moderator access required'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    # Only one question can be staged at a time
    if not question.is_staged:
        Question.objects.filter(event=question.event).update(is_staged=False)
        question.is_staged = True
    else:
        question.is_staged = False
    
    question.save()
    
    return Response({
        'success': True,
        'data': {'isStaged': question.is_staged},
        'message': f'Question {"staged" if question.is_staged else "unstaged"}'
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def manage_event_moderators(request, event_id):
    """Add or remove moderators from an event"""
    event = get_object_or_404(Event, id=event_id)
    user = request.user
    
    # Only existing moderators can manage moderators
    if not event.can_user_moderate(user):
        return Response(
            {'success': False, 'message': 'You do not have permission to manage moderators'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    action = request.data.get('action')  # 'add' or 'remove'
    moderator_emails = request.data.get('moderator_emails', [])
    
    if action == 'add':
        # Add moderators
        added_count = 0
        for email in moderator_emails:
            try:
                moderator = User.objects.get(email=email)
                event.moderators.add(moderator)
                added_count += 1
            except User.DoesNotExist:
                pass  # Skip non-existent users
        
        return Response({
            'success': True,
            'message': f'Added {added_count} moderators',
            'data': EventSerializer(event, context={'request': request}).data
        })
    
    elif action == 'remove':
        # Remove moderators (but not the creator)
        removed_count = 0
        for email in moderator_emails:
            try:
                moderator = User.objects.get(email=email)
                # Don't remove the creator
                if moderator != event.created_by:
                    event.moderators.remove(moderator)
                    removed_count += 1
            except User.DoesNotExist:
                pass  # Skip non-existent users
        
        return Response({
            'success': True,
            'message': f'Removed {removed_count} moderators',
            'data': EventSerializer(event, context={'request': request}).data
        })
    
    else:
        return Response(
            {'success': False, 'message': 'Invalid action. Use "add" or "remove"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def microsoft_oauth_login(request):
    """Microsoft Entra ID OAuth login endpoint"""
    code = request.data.get('code')
    if not code:
        return Response({
            'success': False,
            'message': 'Authorization code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Exchange code for user information
        # This is a placeholder - you'll need to implement actual OAuth flow
        # For now, we'll simulate getting user info from Microsoft
        
        # In a real implementation, you would:
        # 1. Exchange code for access token with Microsoft
        # 2. Get user profile from Microsoft Graph API
        # 3. Create or update user in database
        
        # Simulated Microsoft user data (replace with actual OAuth implementation)
        microsoft_user_data = {
            'id': 'ms-' + request.data.get('user_id', 'unknown'),
            'email': request.data.get('email', ''),
            'name': request.data.get('name', ''),
            'tenant_id': request.data.get('tenant_id', '')
        }
        
        # Find or create user based on Microsoft ID
        user, created = User.objects.get_or_create(
            microsoft_id=microsoft_user_data['id'],
            defaults={
                'email': microsoft_user_data['email'],
                'name': microsoft_user_data['name'],
                'username': microsoft_user_data['email'],
                'role': 'user',
                'is_active': True,
                'is_anonymous': False
            }
        )
        
        # Update user info if it changed
        if not created:
            user.email = microsoft_user_data['email']
            user.name = microsoft_user_data['name']
            user.save()
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            },
            'message': 'Microsoft OAuth login successful'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Microsoft OAuth login failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def microsoft_oauth_url(request):
    """Get Microsoft OAuth authorization URL"""
    # Microsoft OAuth configuration
    tenant_id = "your-tenant-id"  # Replace with actual tenant ID
    client_id = "your-client-id"  # Replace with actual client ID
    redirect_uri = request.build_absolute_uri('/api/auth/microsoft/callback/')
    
    # Microsoft OAuth authorization URL
    auth_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid email profile"
        f"&state=12345"  # Add CSRF protection in production
    )
    
    return Response({
        'success': True,
        'data': {
            'auth_url': auth_url,
            'redirect_uri': redirect_uri
        }
    })

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_user_exists(request):
    """Check if a user exists in the database"""
    email = request.data.get('email')
    if not email:
        return Response({
            'success': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = User.objects.filter(email=email).exists()
    return Response({
        'success': True,
        'data': {'exists': exists}
    })