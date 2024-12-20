# Generated by Django 4.1.13 on 2024-12-12 10:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mail_service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.TextField(verbose_name='收件人')),
                ('subject', models.CharField(max_length=200, verbose_name='邮件主题')),
                ('content', models.TextField(verbose_name='邮件内容')),
                ('from_email', models.CharField(max_length=100, verbose_name='发件人')),
                ('schedule_time', models.TimeField(verbose_name='发送时间')),
                ('repeat_type', models.CharField(choices=[('none', '不重复'), ('daily', '每天'), ('weekly', '每周'), ('monthly', '每月')], default='none', max_length=10, verbose_name='重复类型')),
                ('week_days', models.CharField(blank=True, max_length=20, null=True, verbose_name='每周发送日期')),
                ('month_day', models.IntegerField(blank=True, null=True, verbose_name='每月发送日期')),
                ('next_run', models.DateTimeField(verbose_name='下次运行时间')),
                ('status', models.CharField(choices=[('active', '活动'), ('paused', '暂停'), ('completed', '完成')], default='active', max_length=10, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '邮件定时任务',
                'verbose_name_plural': '邮件定时任务',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='emailhistory',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mail_service.emailschedule', verbose_name='定时任务'),
        ),
    ]
