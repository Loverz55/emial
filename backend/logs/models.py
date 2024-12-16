from django.db import models
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()

class SystemLog(models.Model):
    LOG_TYPES = (
        ('login', '登录'),
        ('logout', '登出'),
        ('email', '邮件操作'),
        ('template', '模板操作'),
        ('schedule', '定时任务'),
        ('system', '系统操作'),
        ('api', 'API调用'),
        ('error', '系统错误'),
    )
    
    LOG_LEVELS = (
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('critical', '严重'),
    )

    STATUS_CHOICES = (
        ('success', '成功'),
        ('failed', '失败'),
        ('pending', '处理中'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作用户')
    type = models.CharField('日志类型', max_length=20, choices=LOG_TYPES, db_index=True, default='system')
    level = models.CharField('日志级别', max_length=10, choices=LOG_LEVELS, default='info', db_index=True)
    action = models.CharField('操作行为', max_length=200, default='系统操作')
    content = models.TextField('详细内容', blank=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='success', db_index=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.CharField('User Agent', max_length=500, blank=True)
    request_method = models.CharField('请求方法', max_length=10, blank=True)
    request_path = models.CharField('请求路径', max_length=255, blank=True)
    request_body = models.TextField('请求内容', blank=True)
    response_code = models.IntegerField('响应代码', null=True, blank=True)
    response_body = models.TextField('响应内容', blank=True)
    execution_time = models.FloatField('执行时间(ms)', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = '系统日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'type', 'level', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        
    def __str__(self):
        return f"{self.get_type_display()}-{self.action}"

    def get_level_color(self):
        """获取日志级别对应的颜色"""
        colors = {
            'info': '#2196F3',
            'warning': '#FFC107',
            'error': '#F44336',
            'critical': '#9C27B0'
        }
        return colors.get(self.level, '#757575')

    def get_status_color(self):
        """获取状态对应的颜色"""
        colors = {
            'success': '#4CAF50',
            'failed': '#F44336',
            'pending': '#FFC107'
        }
        return colors.get(self.status, '#757575')

    def colored_level(self):
        """返回带颜色的日志级别"""
        return format_html(
            '<span style="color: {};">{}</span>',
            self.get_level_color(),
            self.get_level_display()
        )
    colored_level.short_description = '日志级别'

    def colored_status(self):
        """返回带颜色的状态"""
        return format_html(
            '<span style="color: {};">{}</span>',
            self.get_status_color(),
            self.get_status_display()
        )
    colored_status.short_description = '状态'

    @property
    def short_content(self):
        """返回截断的内容预览"""
        return (self.content[:100] + '...') if len(self.content) > 100 else self.content