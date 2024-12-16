#!/bin/bash

# 启动 Redis（如果没有运行）
redis-server &

# 等待 Redis 启动
sleep 2

# 启动 Django 开发服务器
python manage.py runserver &

# 启动 Celery Worker
celery -A email_automation worker -l info &

# 启动 Celery Beat
celery -A email_automation beat -l info &

# 等待所有后台进程完成
wait 