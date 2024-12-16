from django.db import models
from django.contrib.auth import get_user_model
from tasks.models import EmailTask

User = get_user_model()

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(EmailTask, on_delete=models.CASCADE)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'histories'

    def __str__(self):
        return f"{self.task.subject} - {self.created_at}" 