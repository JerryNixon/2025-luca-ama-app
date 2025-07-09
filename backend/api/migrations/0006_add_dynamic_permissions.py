# Manual migration for adding dynamic permissions
# Generated manually to avoid manager issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_fix_user_manager'),
    ]

    operations = [
        # Add new fields to User model
        migrations.AddField(
            model_name='user',
            name='microsoft_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        
        # Add new fields to Event model
        migrations.AddField(
            model_name='event',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='invite_link',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        
        # Update User role choices to include admin
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('moderator', 'Moderator'), 
                    ('presenter', 'Presenter'), 
                    ('user', 'User')
                ], 
                default='user', 
                max_length=20
            ),
        ),
    ]
