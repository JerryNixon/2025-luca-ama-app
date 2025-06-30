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
    """List events and create new events"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Return events where user is creator, moderator, or participant
        return Event.objects.filter(
            Q(created_by=user) | 
            Q(moderators=user) | 
            Q(participants=user)
        ).distinct().annotate(
            question_count=Count('questions')
        )
    
    def perform_create(self, serializer):
        # Generate unique share link
        share_link = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        event = serializer.save(
            created_by=self.request.user,
            share_link=share_link
        )
        # Add creator as moderator
        event.moderators.add(self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete specific event"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(
            Q(created_by=user) | 
            Q(moderators=user) | 
            Q(participants=user)
        )

@api_view(['POST'])
def join_event_view(request, share_link):
    """Join event via share link"""
    event = get_object_or_404(Event, share_link=share_link)
    event.participants.add(request.user)
    return Response({
        'success': True,
        'data': EventSerializer(event).data,
        'message': f'Successfully joined {event.name}'
    })

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
        
        # Check if user has access to this event
        user = self.request.user
        if not (event.created_by == user or 
                user in event.moderators.all() or 
                user in event.participants.all()):
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
        
        # Check permissions
        if (question.author != user and 
            user not in question.event.moderators.all() and
            question.event.created_by != user):
            return Response({'success': False, 'message': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

# ============================================================================
# VOTING VIEWS
# ============================================================================

@api_view(['POST'])
def upvote_question_view(request, question_id):
    """Upvote or remove upvote from question"""
    question = get_object_or_404(Question, id=question_id)
    user = request.user
    
    # Check if user has access to this event
    if not (question.event.created_by == user or 
            user in question.event.moderators.all() or 
            user in question.event.participants.all()):
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
    
    # Check moderator permissions
    if (question.event.created_by != user and 
        user not in question.event.moderators.all()):
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
    
    # Check moderator permissions
    if (question.event.created_by != user and 
        user not in question.event.moderators.all()):
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