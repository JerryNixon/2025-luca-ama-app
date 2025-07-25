from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

# User class
class User(AbstractUser):
    """Extended User model with AMA-specific fields"""
    USER_ROLES = [
        ('admin', 'Admin'),         # System administrator
        ('moderator', 'Moderator'), # Legacy global moderator
        ('presenter', 'Presenter'), # Legacy presenter
        ('user', 'User'),           # Regular user
    ]
    
    AUTH_SOURCES = [
        ('manual', 'Manual Database'),
        ('microsoft', 'Microsoft Entra ID'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    is_anonymous = models.BooleanField(default=False)
    
    # New fields for Microsoft Entra ID integration
    microsoft_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    is_admin = models.BooleanField(default=False)  # System admin flag
    auth_source = models.CharField(max_length=20, choices=AUTH_SOURCES, default='manual')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    def can_create_events(self):
        """Check if user can create events - now everyone can"""
        return True  # Universal access model
    
    def is_system_admin(self):
        """Check if user is system administrator"""
        return self.is_admin or self.role == 'admin'
    
    def get_accessible_events(self):
        """Get all events this user can access"""
        from django.db.models import Q
        
        # User can access events they:
        # 1. Created
        # 2. Are moderators of
        # 3. Are participants of (joined via link)
        # 4. Are public (but only if they're participants)
        
        return Event.objects.filter(
            Q(created_by=self) |  # Created by user
            Q(moderators=self) |  # User is moderator
            Q(participants=self)  # User is participant
        ).distinct()
    
    def get_role_in_event(self, event):
        """Get user's role in a specific event"""
        return event.get_user_role_in_event(self)

# Event class
class Event(models.Model):
    """AMA Event/Session model with dynamic permissions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    open_date = models.DateTimeField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    moderators = models.ManyToManyField(User, related_name='moderated_events', blank=True)
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)
    share_link = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # New fields for enhanced permission system
    is_public = models.BooleanField(default=False)  # Whether event is publicly discoverable
    invite_link = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Unique invite link
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def generate_share_link(self):
        """Generate a unique, secure share link for this event"""
        import secrets
        import string
        
        if self.share_link:
            return self.share_link
            
        # Generate a 12-character random string (alphanumeric)
        characters = string.ascii_letters + string.digits
        while True:
            share_code = ''.join(secrets.choice(characters) for _ in range(12))
            # Ensure uniqueness
            if not Event.objects.filter(share_link=share_code).exists():
                self.share_link = share_code
                self.save()
                return share_code
    
    def get_share_url(self, base_url='http://localhost:3001'):
        """Get the full share URL for this event"""
        if not self.share_link:
            self.generate_share_link()
        return f"{base_url}/join/{self.share_link}"
    
    def is_currently_active(self):
        """Check if the event is currently active (not expired)"""
        from django.utils import timezone
        now = timezone.now()
        
        # Event is active if:
        # 1. It has started (open_date is None or in the past)
        # 2. It hasn't closed (close_date is None or in the future)
        if self.open_date and self.open_date > now:
            return False  # Event hasn't started yet
        
        if self.close_date and self.close_date < now:
            return False  # Event has ended
        
        return True
    
    def can_user_moderate(self, user):
        """Check if user can moderate this event"""
        return (user.is_system_admin() or 
                self.created_by == user or 
                user in self.moderators.all())
    
    def can_user_access(self, user):
        """Check if user can access this event"""
        # User can access if they have any role in the event
        return self.get_user_role_in_event(user) != 'no_access'
    
    def get_user_role_in_event(self, user):
        """Get user's role in this specific event"""
        if user.is_system_admin():
            return 'admin'
        elif self.created_by == user:
            return 'creator'
        elif user in self.moderators.all():
            return 'moderator'
        elif user in self.participants.all():
            return 'participant'
        else:
            return 'no_access'
    
    def get_user_permissions(self, user):
        """Get detailed permissions for a user in this event"""
        role = self.get_user_role_in_event(user)
        
        if role == 'no_access':
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
        
        # Base permissions for all users with access
        permissions = {
            'can_view': True,
            'can_ask_questions': True,
            'can_vote': True,
            'can_moderate': False,
            'can_edit_event': False,
            'can_delete_event': False,
            'can_add_moderators': False,
            'view_type': 'user'
        }
        
        # Enhanced permissions for moderators and creators
        if role in ['creator', 'moderator', 'admin']:
            permissions.update({
                'can_moderate': True,
                'can_edit_event': True,
                'can_add_moderators': True,
                'view_type': 'moderator'
            })
        
        # Creator and admin can delete events
        if role in ['creator', 'admin']:
            permissions['can_delete_event'] = True
        
        return permissions
# Question class
class Question(models.Model):
    """Question model for AMA sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    is_anonymous = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    is_answered = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_staged = models.BooleanField(default=False)
    presenter_notes = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, null=True)
    parent_question = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='grouped_questions')
    tags = models.TextField(default='[]', blank=True)  # Store JSON as text for SQL Server compatibility
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ==========================================================================
    # FABRIC AI FIELDS - Native Integration with Microsoft Fabric AI
    # ==========================================================================
    
    # Primary embedding storage using Fabric's native vector format
    # This field stores the embedding in binary format optimized for Fabric's VECTOR_DISTANCE function
    # Binary storage is more efficient than JSON for large-scale operations
    embedding_vector = models.BinaryField(
        null=True,                              # Allow null for questions not yet processed
        blank=True,                             # Allow empty in forms
        help_text="Fabric native vector embedding in binary format for optimal performance"
    )
    
    # Backup embedding storage in JSON format
    # This provides compatibility with external tools and easier debugging
    # JSON format is human-readable but less efficient for similarity operations
    embedding_json = models.TextField(
        blank=True,                             # Allow empty strings
        null=True,                              # Allow null values
        help_text="JSON representation of embedding vector for compatibility and debugging"
    )

    # AI processing status tracking
    # This field tracks whether Fabric AI has processed this question
    # Helps prevent duplicate processing and enables batch operations
    fabric_ai_processed = models.BooleanField(
        default=False,                          # Default to unprocessed
        help_text="Indicates whether Fabric AI processing has been completed"
    )
    # Vector indexing status for performance optimization
    # Tracks whether this question's embedding is included in Fabric's vector index
    # Important for monitoring similarity search performance
    fabric_similarity_indexed = models.BooleanField(
        default=False,                          # Default to not indexed
        help_text="Indicates whether the embedding vector is properly indexed in Fabric"
    )
    # AI confidence score for quality assessment
    # Fabric AI provides confidence scores for its operations
    # Higher scores indicate more reliable AI results
    ai_confidence_score = models.FloatField(
        null=True,                              # Allow null for unprocessed questions
        blank=True,                             # Allow empty in forms
        help_text="Fabric AI confidence score (0.0 to 1.0, higher = more confident)"
    )
    # Semantic clustering identifier
    # Fabric's AI.CLUSTER function assigns questions to semantic groups
    # This helps moderators organize questions by topic automatically
    fabric_semantic_cluster = models.CharField(
        max_length=100,                         # Reasonable length for cluster names
        blank=True,                             # Allow empty strings
        null=True,                              # Allow null values
        help_text="Semantic cluster assigned by Fabric AI for automatic grouping"
    )
        # ==========================================================================
    # EXTENDED AI METADATA FIELDS
    # ==========================================================================
    
    # Sentiment analysis result from Fabric AI
    # Tracks the emotional tone of the question (positive, negative, neutral)
    # Helps moderators prioritize urgent or sensitive questions
    ai_sentiment = models.CharField(
        max_length=20,                          # Enough for sentiment labels
        blank=True,                             # Allow empty strings
        null=True,                              # Allow null values
        choices=[                               # Predefined sentiment options
            ('positive', 'Positive'),
            ('negative', 'Negative'),
            ('neutral', 'Neutral'),
            ('mixed', 'Mixed'),
        ],
        help_text="Sentiment analysis result from Fabric AI"
    )
    
    # Topic extraction results from Fabric AI
    # Stores automatically identified topics in JSON format
    # Helps with question categorization and analytics
    ai_topics = models.TextField(
        blank=True,                             # Allow empty strings
        null=True,                              # Allow null values
        help_text="JSON array of topics extracted by Fabric AI"
    )
    
    # Automatic categorization by Fabric AI
    # Assigns questions to predefined categories for organization
    # Supports filtering and analytics by question type
    ai_category = models.CharField(
        max_length=50,                          # Reasonable length for categories
        blank=True,                             # Allow empty strings
        null=True,                              # Allow null values
        help_text="Automatic category assigned by Fabric AI"
    )
    
    # Processing timestamps for performance monitoring
    # Tracks when AI processing started and completed
    # Helps identify performance bottlenecks and optimization opportunities
    ai_processing_started_at = models.DateTimeField(
        null=True,                              # Allow null for unprocessed questions
        blank=True,                             # Allow empty in forms
        help_text="Timestamp when AI processing began"
    )
    
    ai_processing_completed_at = models.DateTimeField(
        null=True,                              # Allow null for incomplete processing
        blank=True,                             # Allow empty in forms
        help_text="Timestamp when AI processing completed"
    )
    
    # Error tracking for AI operations
    # Stores any errors that occurred during AI processing
    # Helps with debugging and system monitoring
    ai_processing_error = models.TextField(
        blank=True,                             # Allow empty strings
        null=True,                              # Allow null values
        help_text="Error message if AI processing failed"
    )
    class Meta:
        """
        Model metadata including ordering and database indexes
        """
        ordering = ['-upvotes', '-created_at']  # Sort by popularity then recency
        
        # Database indexes for performance optimization
        indexes = [
            # Standard indexes for common queries
            models.Index(fields=['event', 'created_at']),           # Event timeline queries
            models.Index(fields=['is_starred', 'is_staged']),       # Moderator queries
            models.Index(fields=['author', 'created_at']),          # User question history
            
            # AI-specific indexes for Fabric operations
            models.Index(fields=['fabric_ai_processed', 'event']),   # AI processing status
            models.Index(fields=['fabric_semantic_cluster', 'event']), # Semantic clustering
            models.Index(fields=['ai_confidence_score']),            # Quality filtering
            models.Index(fields=['ai_sentiment', 'event']),         # Sentiment analysis
            models.Index(fields=['ai_category', 'event']),          # Category filtering
            
            # Performance monitoring indexes
            models.Index(fields=['ai_processing_completed_at']),     # Processing timeline
        ]
        
        # Constraints to ensure data integrity
        constraints = [
            # Ensure confidence scores are in valid range
            models.CheckConstraint(
                check=models.Q(ai_confidence_score__gte=0.0) & models.Q(ai_confidence_score__lte=1.0),
                name='valid_ai_confidence_score'
            ),
        ]
    def __str__(self):
        return f"Question by {self.author.name}: {self.text[:50]}..."
    def get_ai_processing_duration(self):
        """
        Calculate how long AI processing took for this question
        
        Returns:
            timedelta object or None if processing not completed
        """
        if self.ai_processing_started_at and self.ai_processing_completed_at:
            return self.ai_processing_completed_at - self.ai_processing_started_at
        return None
    
    def has_valid_embedding(self):
        """
        Check if this question has a valid embedding for similarity operations
        
        Returns:
            Boolean indicating whether the question can be used for similarity matching
        """
        return bool(self.embedding_vector and self.fabric_ai_processed)
    
    def get_similarity_metadata(self):
        """
        Get metadata about this question's AI processing for debugging
        
        Returns:
            Dictionary with AI processing information
        """
        return {
            'fabric_ai_processed': self.fabric_ai_processed,
            'similarity_indexed': self.fabric_similarity_indexed,
            'confidence_score': self.ai_confidence_score,
            'semantic_cluster': self.fabric_semantic_cluster,
            'processing_duration': self.get_ai_processing_duration(),
            'has_valid_embedding': self.has_valid_embedding(),
        }
# Vote Class
class Vote(models.Model):
    """Vote tracking for questions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='vote_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['question', 'user']  # Prevent duplicate votes
    
    def __str__(self):
        return f"{self.user.name} voted on: {self.question.text[:30]}..."