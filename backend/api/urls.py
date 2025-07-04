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
    
    # Events
    path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
    path('events/<uuid:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/join/<str:share_link>/', views.join_event_view, name='join-event'),
    
    # Questions
    path('events/<uuid:event_id>/questions/', views.QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<uuid:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    
    # Voting and Actions
    path('questions/<uuid:question_id>/upvote/', views.upvote_question_view, name='upvote-question'),
    path('questions/<uuid:question_id>/star/', views.star_question_view, name='star-question'),
    path('questions/<uuid:question_id>/stage/', views.stage_question_view, name='stage-question'),
]
