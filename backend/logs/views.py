from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import SystemLog
from .serializers import SystemLogSerializer

class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['level', 'user', 'ip_address', 'method']
    search_fields = ['message', 'path']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取日志统计信息"""
        level_stats = SystemLog.objects.values('level').annotate(
            count=Count('id')
        )
        method_stats = SystemLog.objects.values('method').annotate(
            count=Count('id')
        )
        
        return Response({
            'level_stats': level_stats,
            'method_stats': method_stats,
            'total_logs': SystemLog.objects.count()
        }) 