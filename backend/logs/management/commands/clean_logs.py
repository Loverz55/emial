from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from logs.models import SystemLog

class Command(BaseCommand):
    help = '清理指定天数之前的系统日志'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='要保留的日志天数（默认30天）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际删除数据'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # 计算截止日期
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # 获取要删除的日志数量
        logs_to_delete = SystemLog.objects.filter(created_at__lt=cutoff_date)
        count = logs_to_delete.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'试运行模式：将删除 {count} 条 {days} 天前���日志记录'
                )
            )
        else:
            # 执行删除
            logs_to_delete.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'成功删除 {count} 条 {days} 天前的日志记录'
                )
            ) 