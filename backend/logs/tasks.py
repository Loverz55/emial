from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command

@shared_task
def clean_old_logs(days=30):
    """
    清理指定天数之前的系统日志
    :param days: 要保留的日志天数
    """
    try:
        call_command('clean_logs', days=days)
    except Exception as e:
        print(f"清理日志失败: {str(e)}")  # 在生产环境中应该使用proper logging 