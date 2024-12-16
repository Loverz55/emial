from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, time
import requests
from .models import EmailHistory, EmailSchedule, EmailTemplate, EmailImage
from .tasks import send_scheduled_email, send_batch_emails
from django.db.models import Q, F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .serializers import EmailTemplateSerializer, EmailImageSerializer
from django.conf import settings
import os

class SendEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 获取请求数据
            subject = request.data.get('subject')
            content = request.data.get('message')  # 前端使用 message 字段
            recipient = request.data.get('to')  # 前端使用 to 字段
            from_email = request.data.get('from', settings.DEFAULT_FROM_EMAIL)
            
            # 验证必要参数
            if not all([subject, content, recipient]):
                return Response({
                    'error': '缺少必要参数',
                    'detail': {
                        'subject': '邮件主题不能为空' if not subject else None,
                        'content': '邮件内容不能为空' if not content else None,
                        'recipient': '收件人不能为空' if not recipient else None
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理多个收件人的情况
            recipient_list = [email.strip() for email in recipient.split(',') if email.strip()]
            if not recipient_list:
                return Response({
                    'error': '收件人格式错误',
                    'detail': '请输入有效的邮箱地址'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 使用指定的API发送邮件
            for recipient_email in recipient_list:
                try:
                    api_url = f'https://v.api.aa1.cn/api/qqemail/new/?to={recipient_email}&from_mail={from_email}&subject={subject}&message={content}'
                    response = requests.get(api_url)
                    
                    # 记录发送历史
                    EmailHistory.objects.create(
                        user=request.user,
                        recipient=recipient_email,
                        subject=subject,
                        content=content,
                        status='completed' if response.status_code == 200 else 'failed',
                        error_message=str(response.text) if response.status_code != 200 else None
                    )
                except Exception as e:
                    # 记录发送失败
                    EmailHistory.objects.create(
                        user=request.user,
                        recipient=recipient_email,
                        subject=subject,
                        content=content,
                        status='failed',
                        error_message=str(e)
                    )
            
            return Response({
                'message': '邮件发送成功',
                'detail': f'已发送给 {len(recipient_list)} 个收件人'
            })
            
        except Exception as e:
            return Response({
                'error': '邮件发送失败',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmailHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            search = request.query_params.get('search', '')
            
            # 使用 select_related 预加载定时任务信息
            history = EmailHistory.objects.select_related('schedule').filter(
                user=request.user
            )
            
            # 打印原始查询 SQL
            print("\n=== 查询 SQL ===")
            print(history.query)
            
            # 如果有搜索条件
            if search:
                history = history.filter(
                    Q(recipient__icontains=search) |
                    Q(subject__icontains=search)
                )
            
            # 按发送时间倒序排序
            history = history.order_by('-send_time')
            
            # 简单的分页
            start = (page - 1) * page_size
            end = start + page_size
            
            records = history[start:end]
            
            # 打印每条记录的详细信息
            print("\n=== 查询结果 ===")
            for record in records:
                print(f"\n记录 ID: {record.id}")
                print(f"收件人: {record.recipient}")
                print(f"主题: {record.subject}")
                print(f"状态: {record.status}")
                print(f"发送时间: {record.send_time}")
                if record.schedule:
                    print("定时任务信息:")
                    print(f"  - ID: {record.schedule.id}")
                    print(f"  - 重复类型: {record.schedule.repeat_type}")
                    print(f"  - 执行时间: {record.schedule.schedule_time}")
                    print(f"  - 下次执行: {record.schedule.next_run}")
                    print(f"  - 状态: {record.schedule.status}")
                    if record.schedule.week_days:
                        print(f"  - 每周执行日: {record.schedule.week_days}")
                    if record.schedule.month_day:
                        print(f"  - 每月执行日: {record.schedule.month_day}")
                else:
                    print("普通发送（无定时任务）")
            
            total = history.count()
            print(f"\n总记录数: {total}")
            
            # 序列化数据
            data = []
            for record in records:
                record_data = {
                    'id': record.id,
                    'recipient': record.recipient,
                    'subject': record.subject,
                    'content': record.content,
                    'status': record.status,
                    'send_time': record.send_time,
                    'error_message': record.error_message,
                    'schedule': {
                        'id': record.schedule.id,
                        'repeat_type': record.schedule.repeat_type,
                        'schedule_time': record.schedule.schedule_time,
                        'next_run': record.schedule.next_run,
                        'status': record.schedule.status,
                        'week_days': record.schedule.week_days,
                        'month_day': record.schedule.month_day
                    } if record.schedule else None
                }
                data.append(record_data)
            
            # 打印最终返回的数据结构
            print("\n=== 返回数据 ===")
            print(f"数据条数: {len(data)}")
            print(f"数据示例: {data[0] if data else None}")
            
            return Response({
                'total': total,
                'data': data,
                'page': page,
                'page_size': page_size
            })
            
        except Exception as e:
            print(f"\n=== 发生错误 ===")
            print(f"错误类型: {type(e)}")
            print(f"错误信息: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return Response({
                'message': '获取发送记录失败',
                'detail': str(e)
            }, status=400)

class ScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取用户的定时任务列表"""
        try:
            schedules = EmailSchedule.objects.filter(
                user=request.user,
                status='active'
            ).order_by('-created_at')
            
            data = [{
                'id': schedule.id,
                'recipient': schedule.recipient,
                'subject': schedule.subject,
                'schedule_time': schedule.schedule_time,
                'repeat_type': schedule.repeat_type,
                'week_days': schedule.week_days.split(',') if schedule.week_days else None,
                'month_day': schedule.month_day,
                'next_run': schedule.next_run,
                'status': schedule.status
            } for schedule in schedules]
            
            return Response(data)
            
        except Exception as e:
            return Response({
                'message': '获取定时任务失败',
                'detail': str(e)
            }, status=400)
    
    def delete(self, request, schedule_id):
        """删除定时任务"""
        try:
            schedule = EmailSchedule.objects.get(
                id=schedule_id,
                user=request.user
            )
            schedule.status = 'completed'
            schedule.save()
            
            return Response({
                'message': '定时任务已删除'
            })
            
        except EmailSchedule.DoesNotExist:
            return Response({
                'message': '定时任务不存在'
            }, status=404)
        except Exception as e:
            return Response({
                'message': '删除定时任务失败',
                'detail': str(e)
            }, status=400)

class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    
    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        template = self.get_object()
        new_template = EmailTemplate.objects.create(
            name=f"{template.name} (复制)",
            category=template.category,
            description=template.description,
            subject=template.subject,
            content=template.content
        )
        serializer = self.get_serializer(new_template)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class EmailImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('image')
            if not image_file:
                return Response(
                    {'message': '没有上传文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return Response(
                    {'message': '不支持的文件类型'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 检查文件大小
            if image_file.size > settings.MAX_UPLOAD_SIZE:
                return Response(
                    {'message': '文件大小超过限制'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 保存文件
            image = EmailImage.objects.create(image=image_file)
            
            return Response({
                'url': request.build_absolute_uri(image.image.url),
                'message': '上传成功'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 