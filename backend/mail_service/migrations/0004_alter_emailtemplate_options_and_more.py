# Generated by Django 4.1.13 on 2024-12-13 10:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail_service', '0003_emailimage_emailtemplate'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailtemplate',
            options={'ordering': ['-created_at'], 'verbose_name': '邮件模板', 'verbose_name_plural': '邮件模板'},
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='category',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='description',
        ),
        migrations.RemoveField(
            model_name='emailtemplate',
            name='usage_count',
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建用户'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='name',
            field=models.CharField(max_length=100, verbose_name='模板名称'),
        ),
        migrations.CreateModel(
            name='EmailSendLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('success', '成功'), ('failed', '失败'), ('pending', '处理中')], default='pending', max_length=10, verbose_name='发送状态')),
                ('message', models.TextField(blank=True, verbose_name='详细信息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mail_service.emailschedule', verbose_name='关联任务')),
            ],
            options={
                'verbose_name': '发送日志',
                'verbose_name_plural': '发送日志',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='emailsendlog',
            index=models.Index(fields=['schedule', 'status', 'created_at'], name='mail_servic_schedul_bb072b_idx'),
        ),
    ]
