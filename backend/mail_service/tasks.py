from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailSchedule, EmailSendLog, EmailHistory
from logs.utils import log_action
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from celery import chord

User = get_user_model()

def create_mock_request(user):
    """创建一个模拟的request对象用于日志记录"""
    request = HttpRequest()
    request.user = user
    request.META = {
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_USER_AGENT': 'Celery Task'
    }
    return request

@shared_task
def send_single_email(subject, content, from_email, recipient_email, user_id):
    """发送单个邮件的任务"""
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject=subject,
            message=content,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        # 记录发送历史
        EmailHistory.objects.create(
            user=user,
            recipient=recipient_email,
            subject=subject,
            content=content,
            status='completed'
        )
        
        return True
    except Exception as e:
        # 记录发送失败
        EmailHistory.objects.create(
            user=user,
            recipient=recipient_email,
            subject=subject,
            content=content,
            status='failed',
            error_message=str(e)
        )
        return False

@shared_task
def send_batch_emails(subject, content, from_email, recipient_list, user_id):
    """批量发送邮件的任务"""
    # 创建单个邮件发送任务
    tasks = []
    for recipient in recipient_list:
        task = send_single_email.s(
            subject=subject,
            content=content,
            from_email=from_email,
            recipient_email=recipient,
            user_id=user_id
        )
        tasks.append(task)
    
    # 使用chord来并行执行所有任务
    callback = summarize_results.s(user_id=user_id)
    chord(tasks)(callback)

@shared_task
def summarize_results(results, user_id):
    """汇总发送结果"""
    success_count = sum(1 for r in results if r)
    failure_count = len(results) - success_count
    
    user = User.objects.get(id=user_id)
    mock_request = create_mock_request(user)
    
    log_action(
        request=mock_request,
        type='email',
        action='批量发送邮件完成',
        content=f'成功: {success_count}, 失败: {failure_count}',
        level='info' if failure_count == 0 else 'warning'
    )
    
    return {
        'success_count': success_count,
        'failure_count': failure_count
    }

@shared_task
def send_scheduled_email(schedule_id):
    try:
        schedule = EmailSchedule.objects.get(id=schedule_id)
        if not schedule.is_active:
            return

        # 创建模拟request对象用于日志记录
        mock_request = create_mock_request(schedule.user)
        
        try:
            # 发送邮件
            send_mail(
                subject=schedule.subject,
                message=schedule.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[schedule.recipient_email],
                fail_silently=False,
            )
            
            # 记录发送成功
            EmailSendLog.objects.create(
                schedule=schedule,
                status='success',
                message='邮件发送成功'
            )
            
            # 记录系统日志
            log_action(
                request=mock_request,
                type='email',
                action='发送定时邮件',
                content=f'成功发送邮件到 {schedule.recipient_email}'
            )
            
        except Exception as e:
            # 记录发送失败
            EmailSendLog.objects.create(
                schedule=schedule,
                status='failed',
                message=str(e)
            )
            
            # 记录系统日志
            log_action(
                request=mock_request,
                type='email',
                action='发送定时邮件失败',
                content=f'发送邮件到 {schedule.recipient_email} 失败: {str(e)}',
                level='error'
            )
            
            raise e
            
    except EmailSchedule.DoesNotExist:
        # 记录系统日志
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            mock_request = create_mock_request(admin_user)
            log_action(
                request=mock_request,
                type='email',
                action='定时任务错误',
                content=f'未找到ID为 {schedule_id} 的定时任务',
                level='error'
            )