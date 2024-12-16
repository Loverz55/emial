from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class EmailSchedule(models.Model):
    REPEAT_CHOICES = (
        ('none', '不重复'),
        ('daily', '每天'),
        ('weekly', '每周'),
        ('monthly', '每月'),
    )
    
    STATUS_CHOICES = (
        ('active', '活动'),
        ('paused', '暂停'),
        ('completed', '完成'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    recipient = models.TextField(verbose_name='收件人')
    subject = models.CharField(max_length=200, verbose_name='邮件主题')
    content = models.TextField(verbose_name='邮件内容')
    from_email = models.CharField(max_length=100, verbose_name='发件人')
    schedule_time = models.TimeField(verbose_name='发送时间')
    repeat_type = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='none', verbose_name='重复类型')
    week_days = models.CharField(max_length=20, blank=True, null=True, verbose_name='每周发送日期')
    month_day = models.IntegerField(blank=True, null=True, verbose_name='每月发送日期')
    next_run = models.DateTimeField(verbose_name='下次运行时间')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '邮件定时任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.subject} - {self.schedule_time}'

class EmailHistory(models.Model):
    STATUS_CHOICES = (
        ('completed', '发送成功'),
        ('failed', '发送失败'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    schedule = models.ForeignKey(EmailSchedule, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='定时任务')
    recipient = models.EmailField(verbose_name='收件人')
    subject = models.CharField(max_length=200, verbose_name='邮件主题')
    content = models.TextField(verbose_name='邮件内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed', verbose_name='发送状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    send_time = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        verbose_name = '邮件历史'
        verbose_name_plural = verbose_name
        ordering = ['-send_time']
    
    def __str__(self):
        return f'{self.subject} - {self.recipient}' 

class EmailTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('notice', '通知'),
        ('marketing', '营销'),
        ('other', '其他'),
    ]
    
    name = models.CharField('模板名称', max_length=100)
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField('描述', blank=True)
    subject = models.CharField('邮件主题', max_length=200)
    content = models.TextField('邮件内容')
    usage_count = models.IntegerField('使用次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '邮件模板'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class EmailImage(models.Model):
    image = models.ImageField('图片', upload_to='email_images/%Y/%m/')
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '邮件图片'
        verbose_name_plural = verbose_name
        ordering = ['-uploaded_at'] 

class EmailSendLog(models.Model):
    """邮件发送日志"""
    STATUS_CHOICES = (
        ('success', '成功'),
        ('failed', '失败'),
        ('pending', '处理中'),
    )

    schedule = models.ForeignKey(EmailSchedule, on_delete=models.CASCADE, verbose_name='关联任务')
    status = models.CharField('发送状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField('详细信息', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '发送日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['schedule', 'status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.schedule.name} - {self.get_status_display()}" 