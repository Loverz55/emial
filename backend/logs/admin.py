from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path
import csv
from datetime import datetime
from .models import SystemLog

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'colored_level', 'colored_status', 
        'type', 'user', 'action', 'ip_address', 
        'request_method', 'response_code', 'execution_time'
    ]
    list_filter = [
        'type', 'level', 'status', 'request_method',
        ('response_code', admin.EmptyFieldListFilter),
        'user', 'created_at'
    ]
    search_fields = [
        'action', 'content', 'ip_address', 'request_path',
        'user__username', 'user__email'
    ]
    readonly_fields = [
        'created_at', 'execution_time', 'ip_address',
        'user_agent', 'request_method', 'request_path',
        'request_body', 'response_code', 'response_body'
    ]
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'user', 'type', 'level', 'status',
                'action', 'content', 'created_at'
            )
        }),
        ('请求信息', {
            'fields': (
                'ip_address', 'user_agent',
                'request_method', 'request_path',
                'request_body'
            ),
            'classes': ('collapse',)
        }),
        ('响应信息', {
            'fields': (
                'response_code', 'response_body',
                'execution_time'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-csv/', self.export_csv, name='export-logs-csv'),
        ]
        return custom_urls + urls

    def export_csv(self, request):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=system_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        # 写入CSV头部
        writer = csv.writer(response)
        headers = []
        for field in field_names:
            field_object = meta.get_field(field)
            header = field_object.verbose_name or field
            headers.append(header)
        writer.writerow(headers)
        
        # 获取过滤后的数据
        queryset = self.get_queryset(request)
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if value is None:
                    row.append('')
                else:
                    row.append(str(value))
            writer.writerow(row)
        
        return response

    def has_add_permission(self, request):
        return False  # 禁止手动添加日志

    def has_change_permission(self, request, obj=None):
        return False  # 禁止修改日志

    def has_delete_permission(self, request, obj=None):
        # 只允许超级管理员删除日志
        return request.user.is_superuser

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions 