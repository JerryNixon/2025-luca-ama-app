"""
URL Configuration for the AMA API app.
Defines all the API endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.me_view, name='me'),
    path('auth/check-user/', views.check_user_exists, name='check-user-exists'),
    
    # Microsoft OAuth Authentication
    path('auth/microsoft/', views.microsoft_oauth_login, name='microsoft-oauth-login'),
    path('auth/microsoft/url/', views.microsoft_oauth_url, name='microsoft-oauth-url'),
    
    # Events - Order matters! More specific patterns first
    path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
    path('events/join/<str:share_link>/', views.join_event_view, name='join-event'),
    path('events/invite/<str:invite_link>/', views.join_event_by_invite, name='join-event-by-invite'),
    path('events/<uuid:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<uuid:event_id>/moderators/', views.manage_event_moderators, name='manage-event-moderators'),
    
    # Questions
    path('events/<uuid:event_id>/questions/', views.QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<uuid:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    
    # Voting and Actions
    path('questions/<uuid:question_id>/upvote/', views.upvote_question_view, name='upvote-question'),
    path('questions/<uuid:question_id>/star/', views.star_question_view, name='star-question'),
    path('questions/<uuid:question_id>/stage/', views.stage_question_view, name='stage-question'),
    
    # Fabric AI Endpoints - Microsoft Fabric AI Integration
    # Real-time similarity checking for duplicate prevention
    path('events/<uuid:event_id>/ai/similar-questions/', views.check_similar_questions_fabric, name='fabric-similar-questions'),
    
    # AI-powered question clustering for moderators
    path('events/<uuid:event_id>/ai/cluster-questions/', views.cluster_questions_fabric, name='fabric-cluster-questions'),
    
    # Comprehensive AI processing for individual questions
    path('questions/<uuid:question_id>/ai/process/', views.process_question_ai_fabric, name='fabric-process-question'),
]
