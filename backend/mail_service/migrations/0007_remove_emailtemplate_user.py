# Generated by Django 4.1.13 on 2024-12-13 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail_service', '0006_emailtemplate_description_emailtemplate_usage_count_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailtemplate',
            name='user',
        ),
    ]