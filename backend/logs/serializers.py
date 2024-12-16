from rest_framework import serializers
from .models import SystemLog

class SystemLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = SystemLog
        fields = ('id', 'username', 'level', 'level_display', 'message', 
                 'ip_address', 'path', 'method', 'created_at') 