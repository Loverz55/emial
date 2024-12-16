from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import EmailTask
from .serializers import EmailTaskSerializer
from .tasks import send_email_task

class EmailTaskViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_admin:
            return EmailTask.objects.all()
        return EmailTask.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        if task.schedule_time <= timezone.now():
            # 立即发送
            send_email_task.delay(task.id)
        else:
            # 计划发送
            send_email_task.apply_async(
                args=[task.id],
                eta=task.schedule_time
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消任务"""
        task = self.get_object()
        if task.status == 'pending':
            task.status = 'cancelled'
            task.save()
            return Response({'message': '任务已取消'})
        return Response(
            {'error': '只能取消待发送的任务'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取任务统计信息"""
        queryset = self.get_queryset()
        total = queryset.count()
        pending = queryset.filter(status='pending').count()
        completed = queryset.filter(status='completed').count()
        failed = queryset.filter(status='failed').count()

        return Response({
            'total': total,
            'pending': pending,
            'completed': completed,
            'failed': failed
        }) 