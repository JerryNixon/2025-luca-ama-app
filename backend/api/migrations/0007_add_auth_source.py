# Generated manually to fix auth_source field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_add_dynamic_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_source',
            field=models.CharField(choices=[('manual', 'Manual Database'), ('microsoft', 'Microsoft Entra ID')], default='manual', max_length=20),
        ),
    ]
