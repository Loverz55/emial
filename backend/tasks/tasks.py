from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailTask
from history.models import History

@shared_task
def send_email_task(task_id):
    """发送邮件任务"""
    try:
        # 获取任务
        task = EmailTask.objects.get(id=task_id)
        if task.status != 'pending':
            return
        
        # 更新状态为发送中
        task.status = 'sending'
        task.save()

        # 获取收件人列表
        recipients = task.get_recipients_list()
        success_count = 0
        failed_count = 0
        error_messages = []

        # 发送邮件
        for recipient in recipients:
            try:
                send_mail(
                    subject=task.subject,
                    message=task.content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient],
                    fail_silently=False,
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                error_messages.append(f"{recipient}: {str(e)}")

        # 更新任务状态
        task.status = 'completed' if failed_count == 0 else 'failed'
        task.save()

        # 创建历史记录
        History.objects.create(
            user=task.user,
            task=task,
            success_count=success_count,
            failed_count=failed_count,
            error_message='\n'.join(error_messages)
        )

    except EmailTask.DoesNotExist:
        return
    except Exception as e:
        if task:
            task.status = 'failed'
            task.save()
            History.objects.create(
                user=task.user,
                task=task,
                success_count=0,
                failed_count=len(task.get_recipients_list()),
                error_message=str(e)
            )

@shared_task
def clean_old_tasks():
    """清理30天前的已完成任务"""
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    EmailTask.objects.filter(
        created_at__lt=thirty_days_ago,
        status__in=['completed', 'failed']
    ).delete() 