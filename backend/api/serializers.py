"""
Serializers for the AMA app API.
Converts Django model instances to/from JSON for API responses.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
import json
from .models import User, Event, Question, Vote


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with new permission fields."""
    can_create_events = serializers.SerializerMethodField()
    is_system_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'is_anonymous', 'microsoft_id', 
                 'is_admin', 'can_create_events', 'is_system_admin']
        read_only_fields = ['id', 'microsoft_id', 'is_admin']
    
    def get_can_create_events(self, obj):
        return obj.can_create_events()
    
    def get_is_system_admin(self, obj):
        return obj.is_system_admin()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
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
    """Serializer for Event model with dynamic permissions."""
    moderators = UserSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()  # Full URL for sharing
    
    # New permission fields
    user_role_in_event = serializers.SerializerMethodField()
    can_user_moderate = serializers.SerializerMethodField()
    can_user_access = serializers.SerializerMethodField()
    is_created_by_user = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    
    # Fields for moderator assignment
    moderator_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False,
        help_text="List of email addresses to assign as moderators"
    )
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'open_date', 'close_date', 'created_by', 
                 'moderators', 'participants', 'share_link', 'share_url', 'is_active',
                 'created_at', 'updated_at', 'question_count', 'is_public',
                 'invite_link', 'user_role_in_event', 'can_user_moderate',
                 'can_user_access', 'is_created_by_user', 'user_permissions',
                 'moderator_emails']
        read_only_fields = ['id', 'created_at', 'updated_at', 'share_link', 'share_url', 'invite_link']
    
    def get_question_count(self, obj):
        return obj.questions.count()
    
    def get_share_url(self, obj):
        """Get the full share URL for this event"""
        from django.conf import settings
        import urllib.parse
        
        request = self.context.get('request')
        
        # Method 1: Use environment variable if set (most reliable)
        if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
            return obj.get_share_url(settings.FRONTEND_URL)
        
        # Method 2: Try to detect from request headers
        if request:
            # Check Origin header first (for CORS requests from frontend)
            origin = request.META.get('HTTP_ORIGIN')
            if origin:
                return obj.get_share_url(origin)
            
            # Check Referer header (when navigating from frontend pages)
            referer = request.META.get('HTTP_REFERER')
            if referer:
                try:
                    parsed = urllib.parse.urlparse(referer)
                    frontend_url = f"{parsed.scheme}://{parsed.netloc}"
                    return obj.get_share_url(frontend_url)
                except:
                    pass
        
        # Method 3: Fallback to default development port
        return obj.get_share_url('http://localhost:3000')
    
    def get_user_role_in_event(self, obj):
        """Get current user's role in this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_user_role_in_event(request.user)
        return 'no_access'
    
    def get_can_user_moderate(self, obj):
        """Check if current user can moderate this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_user_moderate(request.user)
        return False
    
    def get_can_user_access(self, obj):
        """Check if current user can access this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_user_access(request.user)
        return False
    
    def get_is_created_by_user(self, obj):
        """Check if current user created this event"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.created_by == request.user
        return False
    
    def get_user_permissions(self, obj):
        """Get detailed permissions for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_user_permissions(request.user)
        return {
            'can_view': False,
            'can_ask_questions': False,
            'can_vote': False,
            'can_moderate': False,
            'can_edit_event': False,
            'can_delete_event': False,
            'can_add_moderators': False,
            'view_type': 'no_access'
        }
    
    def create(self, validated_data):
        """Override create to handle moderator assignment and share link generation"""
        moderator_emails = validated_data.pop('moderator_emails', [])
        event = super().create(validated_data)
        
        # Generate share link automatically
        event.generate_share_link()
        
        # Assign moderators if emails provided
        if moderator_emails:
            self._assign_moderators(event, moderator_emails)
        
        return event
    
    def update(self, instance, validated_data):
        """Override update to handle moderator assignment"""
        moderator_emails = validated_data.pop('moderator_emails', None)
        event = super().update(instance, validated_data)
        
        # Update moderators if emails provided
        if moderator_emails is not None:
            # Only moderators can change moderator assignments
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                if instance.can_user_moderate(request.user):
                    self._assign_moderators(event, moderator_emails)
        
        return event
    
    def _assign_moderators(self, event, moderator_emails):
        """Helper method to assign moderators by email"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Clear existing moderators (except creator)
        event.moderators.clear()
        
        # Always add creator as moderator
        if event.created_by:
            event.moderators.add(event.created_by)
        
        # Add additional moderators
        for email in moderator_emails:
            try:
                user = User.objects.get(email=email)
                event.moderators.add(user)
            except User.DoesNotExist:
                # Skip non-existent users - could log this or handle differently
                pass


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new events."""
    
    class Meta:
        model = Event
        fields = ['id', 'name', 'created_by_id', 'open_date', 
                  'close_date', 'share_link']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    author = UserSerializer(read_only=True)
    upvotes = serializers.SerializerMethodField()
    has_user_upvoted = serializers.SerializerMethodField()
    grouped_questions = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'event', 'text', 'author', 'is_anonymous', 'upvotes',
                 'has_user_upvoted', 'is_answered', 'is_starred', 'is_staged',
                 'presenter_notes', 'ai_summary', 'parent_question', 
                 'grouped_questions', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'event', 'author', 'upvotes', 'has_user_upvoted', 
                           'grouped_questions', 'created_at', 'updated_at']
    
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
    
    def get_tags(self, obj):
        """Convert tags string to JSON array."""
        try:
            return json.loads(obj.tags) if obj.tags else []
        except json.JSONDecodeError:
            return []
    
    def create(self, validated_data):
        """Handle tags conversion during creation."""
        tags_data = validated_data.pop('tags', [])
        if isinstance(tags_data, list):
            validated_data['tags'] = json.dumps(tags_data)
        question = Question.objects.create(**validated_data)
        return question
    
    def update(self, instance, validated_data):
        """Handle tags conversion during update."""
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None and isinstance(tags_data, list):
            validated_data['tags'] = json.dumps(tags_data)
        return super().update(instance, validated_data)


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


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model."""
    class Meta:
        model = Vote
        fields = ['id', 'question', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
