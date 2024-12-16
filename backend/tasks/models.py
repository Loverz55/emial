from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailTask(models.Model):
    STATUS_CHOICES = (
        ('pending', '待发送'),
        ('sending', '发送中'),
        ('completed', '已完成'),
        ('failed', '失败')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    recipients = models.TextField()  # 存储邮件接收者列表，用逗号分隔
    schedule_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.status}"

    def get_recipients_list(self):
        return [email.strip() for email in self.recipients.split(',')] 