 # You need to create this new file with all the serializers that convert your Django models to/from JSON:

from rest_framework import serializers
from .models import User, Event, Question, Vote
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_anonymous']
        read_only_fields = ['id']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

class EventSerializer(serializers.ModelSerializer):
    moderators = UserSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'open_date', 'close_date', 'created_by', 
                 'moderators', 'participants', 'share_link', 'is_active',
                 'created_at', 'updated_at', 'question_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'share_link']
    
    def get_question_count(self, obj):
        return obj.questions.count()

class QuestionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    upvotes = serializers.SerializerMethodField()
    has_user_upvoted = serializers.SerializerMethodField()
    grouped_questions = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'event', 'text', 'author', 'is_anonymous', 'upvotes',
                 'has_user_upvoted', 'is_answered', 'is_starred', 'is_staged',
                 'presenter_notes', 'ai_summary', 'parent_question', 
                 'grouped_questions', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'upvotes', 'created_at', 'updated_at']
    
    def get_upvotes(self, obj):
        return obj.vote_records.count()
    
    def get_has_user_upvoted(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.vote_records.filter(user=request.user).exists()
        return False
    
    def get_grouped_questions(self, obj):
        if obj.grouped_questions.exists():
            return QuestionSerializer(obj.grouped_questions.all(), many=True, context=self.context).data
        return []

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'question', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']