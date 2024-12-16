#!/bin/bash

# 启动 Celery Worker
celery -A email_automation worker -l info &

# 启动 Celery Beat
celery -A email_automation beat -l info &

# 等待所有后台进程完成
wait 