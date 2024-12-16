from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models.functions import TruncDate, TruncMonth
from mail_service.models import EmailHistory, EmailTemplate, EmailSchedule, EmailSendLog
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from django.db import models

User = get_user_model()

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        
        # 获取邮件历史记录
        email_history = EmailHistory.objects.filter(user=user)
        
        # 获取定时任务
        scheduled_tasks = EmailSchedule.objects.filter(user=user, status='active')
        
        # 统计数据
        total_sent = email_history.count()
        success_count = email_history.filter(status='completed').count()
        failed_count = email_history.filter(status='failed').count()
        scheduled_count = scheduled_tasks.count()
        
        # 获取今日发送数据
        today_sent = email_history.filter(
            send_time__date=today
        ).count()
        
        # 获取本周数据
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        weekly_stats = email_history.filter(
            send_time__date__gte=week_start,
            send_time__date__lte=week_end
        ).values('status').annotate(
            count=Count('id')
        )
        
        weekly_data = {
            'success': 0,
            'failed': 0
        }
        for stat in weekly_stats:
            if stat['status'] == 'completed':
                weekly_data['success'] = stat['count']
            elif stat['status'] == 'failed':
                weekly_data['failed'] = stat['count']
        
        return Response({
            'totalSent': total_sent,
            'successCount': success_count,
            'failedCount': failed_count,
            'scheduledCount': scheduled_count,
            'todaySent': today_sent,
            'weeklyStats': weekly_data
        })

class RecentTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        limit = int(request.query_params.get('limit', 5))
        
        # 获取最近的邮件发送记录
        recent_emails = EmailHistory.objects.filter(
            user=user
        ).order_by('-send_time')[:limit]
        
        tasks_data = [{
            'id': email.id,
            'subject': email.subject,
            'recipient': email.recipient,
            'status': email.status,
            'send_time': email.send_time,
            'error_message': email.error_message if email.status == 'failed' else None,
            'schedule': {
                'id': email.schedule.id,
                'schedule_time': email.schedule.schedule_time,
                'repeat_type': email.schedule.repeat_type,
                'week_days': email.schedule.week_days.split(',') if email.schedule and email.schedule.week_days else None,
                'month_day': email.schedule.month_day if email.schedule else None,
                'next_run': email.schedule.next_run if email.schedule else None
            } if email.schedule else None
        } for email in recent_emails]
        
        return Response(tasks_data)

class WeeklyStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取当前时间
        now = localtime(timezone.now())
        today = now.date()
        
        # 获取本周的起始日期（周一）
        week_start = today - timedelta(days=today.weekday())
        
        # 初始化本周每天的数据
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        result = []
        
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
            
            # 获取当天的成功发送数量
            success_count = EmailHistory.objects.filter(
                send_time__range=(day_start, day_end),
                status='completed'
            ).count()
            
            # 获取当天的失败发送数量
            failed_count = EmailHistory.objects.filter(
                send_time__range=(day_start, day_end),
                status='failed'
            ).count()
            
            # 构建每天的数据
            result.append({
                'day': weekdays[i],
                'success': success_count,
                'failed': failed_count,
                'date': current_date.strftime('%Y-%m-%d')
            })
        
        print("Weekly stats result:", result)
        return Response(result)

class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        now = localtime(timezone.now())
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        print(f"当前时间: {now}")
        print(f"统计开始时间: {today_start}")
        print(f"统计结束时间: {today_end}")
        
        # 获取总用户数
        total_users = User.objects.count()
        print(f"总用户数: {total_users}")
        
        # 获取今日发送量（直接发送 + 定时任务发送）
        # 直接发送的邮件
        direct_query = EmailHistory.objects.filter(
            send_time__range=(today_start, today_end),
            schedule__isnull=True
        ).only('id', 'send_time', 'schedule')
        today_direct = direct_query.count()
        print(f"直接发送查询SQL: {direct_query.query}")
        print(f"今日直接发送数量: {today_direct}")
        
        # 定时任务发送的邮件
        scheduled_query = EmailHistory.objects.filter(
            send_time__range=(today_start, today_end),
            schedule__isnull=False
        ).only('id', 'send_time', 'schedule')
        today_scheduled = scheduled_query.count()
        print(f"定时任务查询SQL: {scheduled_query.query}")
        print(f"今日定时任务发送数量: {today_scheduled}")
        
        # 查看所有今天的邮件记录
        all_today_mails = EmailHistory.objects.filter(
            send_time__range=(today_start, today_end)
        ).only('id', 'send_time', 'schedule')
        print(f"今日所有邮件查询SQL: {all_today_mails.query}")
        print(f"今日所有邮件数量: {all_today_mails.count()}")
        print("今日邮件列表:")
        for mail in all_today_mails:
            local_time = localtime(mail.send_time)
            print(f"ID: {mail.id}, 发送时间: {local_time}, 定时任务: {mail.schedule_id if mail.schedule else 'None'}")
        
        today_sent = today_direct + today_scheduled
        print(f"今日总发送量: {today_sent}")
        
        # 获取模板总数
        template_count = EmailTemplate.objects.count()
        print(f"模板总数: {template_count}")
        
        # 获取系统日志数量（所有邮件发送记录）
        log_count = EmailHistory.objects.count()
        print(f"总邮件记录数: {log_count}")
        
        # 计算同比增长
        last_week_start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        last_week_end = (now - timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=999999)
        print(f"上周统计时间范围: {last_week_start} - {last_week_end}")
        
        # 用户增长率
        last_week_users = User.objects.filter(
            date_joined__lt=last_week_start
        ).count()
        user_growth = ((total_users - last_week_users) / last_week_users * 100) if last_week_users > 0 else 0
        print(f"上周用户数: {last_week_users}")
        print(f"用户增长率: {user_growth}%")
        
        # 发送量增长率（直接发送 + 定时任务）
        last_week_direct = EmailHistory.objects.filter(
            send_time__range=(last_week_start, last_week_end),
            schedule__isnull=True
        ).count()
        print(f"上周直接发送数量: {last_week_direct}")
        
        last_week_scheduled = EmailHistory.objects.filter(
            send_time__range=(last_week_start, last_week_end),
            schedule__isnull=False
        ).count()
        print(f"上周定时任务发送数量: {last_week_scheduled}")
        
        last_week_sent = last_week_direct + last_week_scheduled
        sent_growth = ((today_sent - last_week_sent) / last_week_sent * 100) if last_week_sent > 0 else 0
        print(f"上周总发送量: {last_week_sent}")
        print(f"发送量增长率: {sent_growth}%")
        
        # 模板增长率
        last_week_templates = EmailTemplate.objects.filter(
            created_at__lt=last_week_start
        ).count()
        template_growth = ((template_count - last_week_templates) / last_week_templates * 100) if last_week_templates > 0 else 0
        print(f"上周模板数: {last_week_templates}")
        print(f"模板增长率: {template_growth}%")
        
        return Response({
            'total_users': total_users,
            'today_sent': today_sent,
            'template_count': template_count,
            'log_count': log_count,
            'trends': {
                'user_growth': round(user_growth, 1),
                'sent_growth': round(sent_growth, 1),
                'template_growth': round(template_growth, 1),
                'log_growth': 0
            }
        })

class AdminChartDataView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            time_range = request.GET.get('range', 'week')
            now = localtime(timezone.now())
            today = now.date()
            
            if time_range == 'week':
                # 获取本周的起始日期（周一）
                start_date = today - timedelta(days=today.weekday())
                date_list = [(start_date + timedelta(days=i)) for i in range(7)]
                labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            elif time_range == 'month':
                start_date = today - timedelta(days=29)
                date_list = [(start_date + timedelta(days=i)) for i in range(30)]
                labels = [d.strftime('%m-%d') for d in date_list]
            else:  # year
                current_year = today.year
                start_date = timezone.datetime(current_year, 1, 1).date()
                date_list = []
                for month in range(1, 13):
                    date_list.append(timezone.datetime(current_year, month, 1).date())
                labels = ['1月', '2月', '3月', '4月', '5月', '6月', 
                         '7月', '8月', '9月', '10月', '11月', '12月']
            
            print(f"时间范围: {time_range}")
            print(f"开始日期: {start_date}")
            print(f"结束日期: {today}")
            
            # 先检查是否有任何邮件记录
            total_emails = EmailHistory.objects.count()
            print(f"数据库中的总邮件数: {total_emails}")
            
            # 检查邮件状态的分布
            status_distribution = EmailHistory.objects.values('status').annotate(
                count=Count('id')
            )
            print(f"邮件状态分布: {status_distribution}")
            
            # 获取发送量统计（包括成功和失败）
            if time_range == 'year':
                # 按月统计
                success_stats = EmailHistory.objects.filter(
                    send_time__year=current_year,
                    status='completed'
                ).annotate(
                    month=TruncMonth('send_time')
                ).values('month').annotate(
                    count=Count('id')
                ).order_by('month')
                
                failed_stats = EmailHistory.objects.filter(
                    send_time__year=current_year,
                    status='failed'
                ).annotate(
                    month=TruncMonth('send_time')
                ).values('month').annotate(
                    count=Count('id')
                ).order_by('month')
                
                # 构建数据
                success_data = [0] * 12
                failed_data = [0] * 12
                
                for stat in success_stats:
                    month_index = stat['month'].month - 1
                    success_data[month_index] = stat['count']
                
                for stat in failed_stats:
                    month_index = stat['month'].month - 1
                    failed_data[month_index] = stat['count']
                
                data = [success_data, failed_data]
            else:
                # 构建每天的时间范围
                success_data = [0] * len(date_list)
                failed_data = [0] * len(date_list)
                
                for i, current_date in enumerate(date_list):
                    # 设置当天的开始和结束时间
                    day_start = timezone.make_aware(datetime.combine(current_date, datetime.min.time()))
                    day_end = timezone.make_aware(datetime.combine(current_date, datetime.max.time()))
                    
                    # 统计成功数量
                    success_count = EmailHistory.objects.filter(
                        send_time__range=(day_start, day_end),
                        status='completed'
                    ).count()
                    success_data[i] = success_count
                    
                    # 统计失败数量
                    failed_count = EmailHistory.objects.filter(
                        send_time__range=(day_start, day_end),
                        status='failed'
                    ).count()
                    failed_data[i] = failed_count
                
                data = [success_data, failed_data]
            
            print(f"处理后的数据: {data}")
            
            return Response({
                'labels': labels,
                'data': data,
                'series': ['成功', '失败']
            })
            
        except Exception as e:
            print(f"图表数据查询错误: {str(e)}")
            return Response(
                {'error': str(e)},
                status=500
            )

class SystemActivitiesView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # 这需要根据实际日志模型来获取系动态
        # 当前返回示例数据
        return Response([
            {
                'content': '新用户 张三 注册成功',
                'time': '10分钟前',
                'type': 'primary',
                'color': '#6366f1'
            },
            {
                'content': '系统更新完成',
                'time': '30分钟前',
                'type': 'success',
                'color': '#10b981'
            },
            {
                'content': '数据库备份成功',
                'time': '1小时前',
                'type': 'info',
                'color': '#6b7280'
            },
            {
                'content': '新增营销模板',
                'time': '2小时前',
                'type': 'warning',
                'color': '#f59e0b'
            }
        ])

class RecentUsersView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        recent_users = User.objects.order_by('-date_joined')[:5]
        return Response([
            {
                'username': user.username,
                'email': user.email,
                'created_at': user.date_joined
            } for user in recent_users
        ])

class PopularTemplatesView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # 获取最近一个月内的模板
        one_month_ago = timezone.now() - timedelta(days=30)
        
        # 获取所有模板并按使用次数和更新时间排序
        templates = EmailTemplate.objects.filter(
            updated_at__gte=one_month_ago
        ).order_by('-usage_count', '-updated_at')[:5]
        
        # 定义标签类型映射
        category_tags = {
            'notice': {'type': 'primary', 'color': '#6366f1'},
            'marketing': {'type': 'success', 'color': '#10b981'},
            'other': {'type': 'info', 'color': '#6b7280'}
        }
        
        template_stats = []
        for template in templates:
            template_stats.append({
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'description': template.description,
                'usage_count': template.usage_count,
                'tagType': category_tags.get(template.category, {}).get('type', 'info'),
                'color': category_tags.get(template.category, {}).get('color', '#6b7280'),
                'created_at': template.created_at,
                'updated_at': template.updated_at
            })
        
        return Response(template_stats) 