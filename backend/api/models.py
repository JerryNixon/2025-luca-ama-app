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
    
    class Meta:
        ordering = ['-upvotes', '-created_at']
    
    def __str__(self):
        return f"Question by {self.author.name}: {self.text[:50]}..."

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