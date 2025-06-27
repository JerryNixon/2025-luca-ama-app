"""
Serializers for the AMA app API.
Converts Django model instances to/from JSON for API responses.
"""

from rest_framework import serializers
from .models import User, Event, Question


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'created_by', 'created_by_id', 
                  'open_date', 'close_date', 'is_active', 'share_link',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new events."""
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'created_by_id', 'open_date', 
                  'close_date', 'share_link']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    author = UserSerializer(read_only=True)
    author_id = serializers.CharField(write_only=True)
    event = EventSerializer(read_only=True)
    event_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'author', 'author_id', 'event', 'event_id',
                  'upvotes', 'is_answered', 'is_anonymous', 'is_starred', 
                  'is_staged', 'presenter_notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new questions."""
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'author_id', 'event_id', 'is_anonymous']


class QuestionVoteSerializer(serializers.Serializer):
    """Serializer for voting on questions."""
    vote_type = serializers.ChoiceField(choices=['upvote'])
    
    
class QuestionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating question status."""
    
    class Meta:
        model = Question
        fields = ['is_answered', 'is_starred', 'is_staged', 'presenter_notes']
