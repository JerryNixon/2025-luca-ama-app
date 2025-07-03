from django.contrib import admin
from .models import User, Event, Question, Vote

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined']
    search_fields = ['name', 'email']
    readonly_fields = ['id', 'date_joined', 'last_login']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'author', 'event', 'upvotes', 'is_answered', 'is_starred']
    list_filter = ['is_answered', 'is_starred', 'is_staged', 'created_at']
    search_fields = ['text', 'author__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at']
