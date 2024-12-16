import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# 设置默认的 Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_automation.settings')

app = Celery('email_automation')

# 使用字符串配置，这样 worker 不需要序列化配置对象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的 Django app 配置中加载任务
app.autodiscover_tasks()

# 配置定时任务
app.conf.beat_schedule = {
    'check-scheduled-emails': {
        'task': 'mail_service.tasks.check_scheduled_emails',
        'schedule': crontab(hour=2, minute=0),
    },
    'clean-old-logs': {
        'task': 'logs.tasks.clean_old_logs',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),
        'args': (30,),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 