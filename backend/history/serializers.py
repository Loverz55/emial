from rest_framework import serializers
from .models import History
from tasks.serializers import EmailTaskSerializer

class HistorySerializer(serializers.ModelSerializer):
    task = EmailTaskSerializer(read_only=True)
    
    class Meta:
        model = History
        fields = ('id', 'user', 'task', 'success_count', 'failed_count', 
                 'error_message', 'created_at')
        read_only_fields = ('user', 'created_at') 