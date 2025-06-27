"""
URL Configuration for the AMA API app.
Defines all the API endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.api_health, name='api_health'),
    
    # User endpoints
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:user_id>/events/', views.user_events, name='user_events'),
    
    # Event endpoints
    path('events/', views.EventListCreateView.as_view(), name='event_list_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:event_id>/questions/', views.event_questions, name='event_questions'),
    
    # Question endpoints
    path('questions/', views.QuestionListCreateView.as_view(), name='question_list_create'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/<int:question_id>/vote/', views.vote_question, name='question_vote'),
]
