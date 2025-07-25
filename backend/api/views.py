from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.conf import settings
from django.utils import timezone
import secrets
import string

from .models import User, Event, Question, Vote
from .serializers import (
    UserSerializer, LoginSerializer, EventSerializer, 
    QuestionSerializer, VoteSerializer
)
# Add this import with your other imports at the top of views.py
from .fabric_ai_service import fabric_ai_service
import json  # For handling JSON data in AI operations
import logging  # For AI operation logging

# Set up logging for this module
logger = logging.getLogger(__name__)
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

@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])  # Allow anonymous access for share links
def join_event_view(request, share_link):
    """Smart join event via share link - handles authentication and registration"""
    try:
        event = get_object_or_404(Event, share_link=share_link)
        
        # Check if event is active
        if not event.is_currently_active():
            return Response({
                'success': False,
                'message': 'This event is no longer available for joining'
            }, status=status.HTTP_410_GONE)
        
        if request.method == 'GET':
            # Return event info for the join page
            return Response({
                'success': True,
                'data': {
                    'event': {
                        'id': str(event.id),
                        'name': event.name,
                        'created_by': event.created_by.name,
                    },
                    'share_link': share_link
                }
            })
        
        elif request.method == 'POST':
            # Handle join logic
            if request.user.is_authenticated:
                # User is already authenticated - add them to event
                if event.can_user_access(request.user):
                    return Response({
                        'success': True,
                        'data': EventSerializer(event, context={'request': request}).data,
                        'message': f'You already have access to {event.name}',
                        'role': event.get_user_role_in_event(request.user),
                        'redirect_url': f'/events/{event.id}'
                    })
                
                # Add user as participant
                event.participants.add(request.user)
                return Response({
                    'success': True,
                    'data': EventSerializer(event, context={'request': request}).data,
                    'message': f'Successfully joined {event.name}',
                    'role': 'participant',
                    'redirect_url': f'/events/{event.id}'
                })
            else:
                # User needs to authenticate/register
                action = request.data.get('action')  # 'login' or 'register'
                email = request.data.get('email')
                password = request.data.get('password')
                name = request.data.get('name')
                
                if not email or not password:
                    return Response({
                        'success': False,
                        'message': 'Email and password are required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if action == 'register':
                    # Register new user
                    if User.objects.filter(email=email).exists():
                        return Response({
                            'success': False,
                            'message': 'User with this email already exists. Please login instead.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    if not name:
                        return Response({
                            'success': False,
                            'message': 'Name is required for registration'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Create new user
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        name=name,
                        auth_source='manual'
                    )
                    
                    # Add user to event as participant
                    event.participants.add(user)
                    
                    # Generate tokens
                    refresh = RefreshToken.for_user(user)
                    
                    return Response({
                        'success': True,
                        'data': {
                            'user': UserSerializer(user).data,
                            'token': str(refresh.access_token),
                            'refresh': str(refresh),
                            'event': EventSerializer(event, context={'request': request}).data
                        },
                        'message': f'Successfully registered and joined {event.name}',
                        'redirect_url': f'/events/{event.id}'
                    })
                
                elif action == 'login':
                    # Login existing user
                    user = authenticate(email=email, password=password)
                    if user:
                        # Add user to event if not already there
                        if not event.can_user_access(user):
                            event.participants.add(user)
                            message = f'Successfully logged in and joined {event.name}'
                        else:
                            message = f'Welcome back! You already have access to {event.name}'
                        
                        # Generate tokens
                        refresh = RefreshToken.for_user(user)
                        
                        return Response({
                            'success': True,
                            'data': {
                                'user': UserSerializer(user).data,
                                'token': str(refresh.access_token),
                                'refresh': str(refresh),
                                'event': EventSerializer(event, context={'request': request}).data
                            },
                            'message': message,
                            'redirect_url': f'/events/{event.id}'
                        })
                    else:
                        return Response({
                            'success': False,
                            'message': 'Invalid email or password'
                        }, status=status.HTTP_401_UNAUTHORIZED)
                
                else:
                    return Response({
                        'success': False,
                        'message': 'Invalid action. Use "login" or "register"'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
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
        """
        Create a new question with automatic Fabric AI processing
        
        This enhanced version automatically processes new questions with Fabric AI
        to generate embeddings, summaries, and metadata for immediate use.
        """
        # Get the event from the URL parameter
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        
        # Verify user has permission to ask questions in this event
        if not event.can_user_access(self.request.user):
            raise PermissionDenied('You do not have permission to ask questions in this event')
        
        # Get the question text for AI processing
        question_text = serializer.validated_data['text']
        
        # Log the question creation
        logger.info(f"Creating new question in event {event_id} with Fabric AI processing")
        
        # Save the question first to get a database ID
        question = serializer.save(
            author=self.request.user,
            event=event
        )
        
        # Record when AI processing starts
        question.ai_processing_started_at = timezone.now()
        question.save()
        
        # Process the question with Fabric AI in the background
        try:
            logger.info(f"Starting Fabric AI processing for new question {question.id}")
            
            # Run comprehensive Fabric AI processing
            ai_results = fabric_ai_service.process_question_with_fabric_ai(
                str(question.id),
                question_text
            )
            
            # Record successful completion
            question.ai_processing_completed_at = timezone.now()
            question.save()
            
            logger.info(f"✅ Fabric AI processing completed for question {question.id}")
            
        except Exception as e:
            # Log AI processing errors but don't fail the question creation
            logger.error(f"❌ Fabric AI processing failed for question {question.id}: {e}")
            
            # Record the error for debugging
            question.ai_processing_error = str(e)
            question.ai_processing_completed_at = timezone.now()
            question.save()
        
        return question

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
    
    # Serialize the full question object for frontend compatibility
    from .serializers import QuestionSerializer
    serializer = QuestionSerializer(question, context={'request': request})
    
    return Response({
        'success': True,
        'data': serializer.data,
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


# =============================================================================
# FABRIC AI ENDPOINTS - Primary AI functionality using Microsoft Fabric
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_similar_questions_fabric(request, event_id):
    """
    Real-time similarity checking using Fabric's native vector functions
    
    This endpoint showcases Fabric's AI capabilities for similarity detection.
    It's called by the frontend while users are typing to show similar questions
    before they submit, reducing duplicate questions during AMA sessions.
    
    Args:
        request: HTTP request containing question_text in POST data
        event_id: UUID of the event to search within
        
    Returns:
        JSON response with similar questions and metadata about Fabric features used
    """
    try:
        # Get the event and verify user has access
        event = get_object_or_404(Event, id=event_id)
        
        # Check if the user can access this event
        # This prevents unauthorized similarity checking across private events
        if not event.can_user_access(request.user):
            return Response({
                'success': False,
                'message': 'Access denied to this event'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Extract the question text from the request
        question_text = request.data.get('question_text', '').strip()
        
        # Don't process very short text to avoid noise
        # Short text doesn't provide enough context for meaningful similarity
        if len(question_text) < 10:
            return Response({
                'success': True,
                'data': {
                    'similar_questions': [],
                    'method': 'fabric_ai',
                    'reason': 'Text too short for similarity analysis'
                }
            })
        
        # Log the similarity check request for monitoring
        logger.info(f"Fabric AI similarity check requested for event {event_id}")
        logger.debug(f"Question text: {question_text[:100]}...")  # Log first 100 chars
        
        # Use Fabric AI service to find similar questions
        # This leverages Fabric's VECTOR_DISTANCE function for optimal performance
        similar_questions = fabric_ai_service.find_similar_questions_fabric(
            question_text,           # Text to find similarities for
            str(event_id),          # Event to search within
            limit=5                 # Maximum number of results to return
        )
        
        # Log the results for debugging and monitoring
        logger.info(f"Fabric AI found {len(similar_questions)} similar questions")
        
        # Return the results with metadata about Fabric features used
        return Response({
            'success': True,
            'data': {
                'similar_questions': similar_questions,
                'method': 'fabric_ai',
                'threshold_used': fabric_ai_service.similarity_threshold,
                'fabric_features_used': [
                    'AI.EMBEDDING() function for vector generation',
                    'VECTOR_DISTANCE() function for similarity calculation',
                    'Native vector indexing for performance',
                    'Semantic clustering integration'
                ],
                'performance_info': {
                    'vector_dimension': fabric_ai_service.fabric_config.get('vector_dimension', 1536),
                    'cache_enabled': fabric_ai_service.enable_caching,
                    'processing_timeout': fabric_ai_service.operation_timeout
                }
            },
            'message': f'Found {len(similar_questions)} similar questions using Fabric AI'
        })
        
    except Event.DoesNotExist:
        # Handle case where event doesn't exist
        logger.warning(f"Similarity check requested for non-existent event: {event_id}")
        return Response({
            'success': False,
            'message': 'Event not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        # Handle any other errors gracefully
        logger.error(f"Fabric similarity check failed for event {event_id}: {e}")
        return Response({
            'success': False,
            'message': 'Failed to check for similar questions using Fabric AI',
            'error_details': str(e) if settings.DEBUG else None  # Only show details in debug mode
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cluster_questions_fabric(request, event_id):
    """
    Use Fabric AI to automatically cluster related questions
    
    This demonstrates Fabric's advanced AI clustering capabilities.
    It groups questions by semantic similarity and topic, helping moderators
    organize large numbers of questions efficiently.
    
    Args:
        request: HTTP request (may contain clustering parameters)
        event_id: UUID of the event to cluster questions for
        
    Returns:
        JSON response with clustering results and statistics
    """
    try:
        # Get the event and verify user has moderator permissions
        event = get_object_or_404(Event, id=event_id)
        
        # Only moderators can perform clustering operations
        # This is a powerful feature that reorganizes questions
        if not event.can_user_moderate(request.user):
            return Response({
                'success': False,
                'message': 'Moderator permissions required for question clustering'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Log the clustering request
        logger.info(f"Fabric AI clustering requested for event {event_id} by user {request.user.email}")
        
        # Use Fabric's AI clustering service
        # This leverages Fabric's AI.CLUSTER function for semantic grouping
        clusters = fabric_ai_service.cluster_questions_fabric(str(event_id))
        
        # Apply the clustering results to the database
        # Group questions based on Fabric AI's clustering analysis
        cluster_count = 0
        questions_grouped = 0
        
        for cluster_name, question_ids in clusters.items():
            # Only create groups with multiple questions
            # Single-question clusters aren't useful for organization
            if len(question_ids) > 1:
                # Use the first question as the parent (primary question)
                parent_id = question_ids[0]
                child_ids = question_ids[1:]  # Remaining questions become children
                
                # Update the database to group these questions
                # This uses Django's ORM for safe database operations
                grouped_count = Question.objects.filter(
                    id__in=child_ids
                ).update(
                    parent_question_id=parent_id  # Set the parent relationship
                )
                
                cluster_count += 1
                questions_grouped += grouped_count
                
                # Log the clustering action for audit trail
                logger.info(f"Created cluster '{cluster_name}' with {len(question_ids)} questions")
        
        # Log the overall clustering results
        logger.info(f"Fabric AI clustering completed: {cluster_count} clusters, {questions_grouped} questions grouped")
        
        return Response({
            'success': True,
            'data': {
                'clusters_created': cluster_count,
                'total_clusters_found': len(clusters),
                'questions_grouped': questions_grouped,
                'clustering_method': 'fabric_ai',
                'fabric_features_used': [
                    'AI.CLUSTER() function for semantic grouping',
                    'Natural language understanding',
                    'Topic similarity analysis',
                    'Semantic relationship detection'
                ],
                'cluster_details': {
                    cluster_name: {
                        'question_count': len(question_ids),
                        'primary_question_id': question_ids[0] if question_ids else None
                    }
                    for cluster_name, question_ids in clusters.items()
                }
            },
            'message': f'Fabric AI successfully created {cluster_count} question clusters'
        })
        
    except Event.DoesNotExist:
        logger.warning(f"Clustering requested for non-existent event: {event_id}")
        return Response({
            'success': False,
            'message': 'Event not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Fabric clustering failed for event {event_id}: {e}")
        return Response({
            'success': False,
            'message': 'Failed to cluster questions using Fabric AI',
            'error_details': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_question_ai_fabric(request, question_id):
    """
    Process a specific question with comprehensive Fabric AI analysis
    
    This endpoint runs the full Fabric AI pipeline on a question:
    - Generates embeddings for similarity matching
    - Creates AI summary for moderator reference
    - Performs sentiment analysis
    - Extracts topics and categories
    - Updates all AI metadata in the database
    
    Args:
        request: HTTP request (may contain processing options)
        question_id: UUID of the question to process
        
    Returns:
        JSON response with detailed AI processing results
    """
    try:
        # Get the question and verify permissions
        question = get_object_or_404(Question, id=question_id)
        event = question.event
        
        # Check if user can moderate this event
        # AI processing is a moderator/admin function
        if not event.can_user_moderate(request.user):
            return Response({
                'success': False,
                'message': 'Moderator permissions required for AI processing'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Log the AI processing request
        logger.info(f"Fabric AI processing requested for question {question_id} by user {request.user.email}")
        
        # Run comprehensive Fabric AI processing
        # This calls our main AI processing pipeline
        ai_results = fabric_ai_service.process_question_with_fabric_ai(
            str(question.id),
            question.text
        )
        
        # Reload the question to get updated AI data
        question.refresh_from_db()
        
        # Log the processing results for monitoring
        logger.info(f"Fabric AI processing completed for question {question_id}")
        logger.info(f"  - Embedding generated: {ai_results.get('embedding_generated', False)}")
        logger.info(f"  - Summary generated: {ai_results.get('summary_generated', False)}")
        logger.info(f"  - Similarity indexed: {ai_results.get('similarity_indexed', False)}")
        logger.info(f"  - Semantic analysis: {ai_results.get('semantic_analysis') is not None}")
        
        return Response({
            'success': True,
            'data': {
                'question_id': str(question.id),
                'ai_processing_results': ai_results,
                'fabric_features_used': [
                    'AI.EMBEDDING() for vector generation',
                    'AI.SUMMARIZE() for question summarization',
                    'AI.ANALYZE_SENTIMENT() for sentiment analysis',
                    'AI.EXTRACT_TOPICS() for topic identification',
                    'AI.CATEGORIZE() for automatic categorization'
                ],
                'updated_question_data': {
                    'ai_summary': question.ai_summary,
                    'ai_sentiment': question.ai_sentiment,
                    'ai_category': question.ai_category,
                    'ai_confidence_score': question.ai_confidence_score,
                    'fabric_semantic_cluster': question.fabric_semantic_cluster,
                    'fabric_ai_processed': question.fabric_ai_processed,
                    'processing_duration': str(question.get_ai_processing_duration()) if question.get_ai_processing_duration() else None
                }
            },
            'message': 'Fabric AI processing completed successfully'
        })
        
    except Question.DoesNotExist:
        logger.warning(f"AI processing requested for non-existent question: {question_id}")
        return Response({
            'success': False,
            'message': 'Question not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Fabric AI processing failed for question {question_id}: {e}")
        return Response({
            'success': False,
            'message': 'Failed to process question with Fabric AI',
            'error_details': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

