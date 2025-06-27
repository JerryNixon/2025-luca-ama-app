from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

# User class
class User(AbstractUser):
    """Extended User model with AMA-specific fields"""
    USER_ROLES = [
        ('moderator', 'Moderator'),
        ('presenter', 'Presenter'), 
        ('user', 'User'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    is_anonymous = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

# Event class
class Event(models.Model):
    """AMA Event/Session model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    open_date = models.DateTimeField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    moderators = models.ManyToManyField(User, related_name='moderated_events', blank=True)
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)
    share_link = models.CharField(max_length=100, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
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
    tags = models.JSONField(default=list, blank=True)
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