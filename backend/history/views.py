from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import History
from .serializers import HistorySerializer

class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return History.objects.all()
        return History.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取历史统计信息"""
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_success=Sum('success_count'),
            total_failed=Sum('failed_count')
        )
        
        return Response({
            'total_success': stats['total_success'] or 0,
            'total_failed': stats['total_failed'] or 0,
            'total_tasks': queryset.count()
        }) 