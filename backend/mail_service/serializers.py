from rest_framework import serializers
from .models import EmailTemplate, EmailImage

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'category', 'description', 'subject', 
                 'content', 'usage_count', 'created_at', 'updated_at']
        read_only_fields = ['usage_count', 'created_at', 'updated_at']

class EmailImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailImage
        fields = ['id', 'image', 'url', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None 