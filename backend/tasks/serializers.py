from rest_framework import serializers
from .models import EmailTask

class EmailTaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EmailTask
        fields = ('id', 'subject', 'content', 'recipients', 'schedule_time', 
                 'status', 'status_display', 'created_at', 'updated_at')
        read_only_fields = ('status', 'created_at', 'updated_at')

    def validate_recipients(self, value):
        emails = [email.strip() for email in value.split(',')]
        for email in emails:
            if not email:
                raise serializers.ValidationError("邮件地址不能为空")
        return value 